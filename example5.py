from mpi4py import MPI
from mpi_master_slave import Master, Slave
from mpi_master_slave import MultiWorkQueue
from enum import IntEnum
import random
import time

from src.io import read_fasta, read_fastq, read_maf, read_from_folder, read_paf, read_dist_paf
from src.utils.lpt import lpt_scheduling
from src.processes import process_target
from src.processes import process_windows
from src.utils.split import split_dict_into_chunks

Tasks = IntEnum('Tasks', 'TASK1 TASK2')


class MyMaster(Master):
    """
    This Master class handles a specific task
    """

    def __init__(self, task, slaves = None):
        super(MyMaster, self).__init__(slaves)
        self.task = task

    def run(self, slave, data):
        args = (self.task, data)
        super(MyMaster, self).run(slave, args)

    def get_data(self, completed_slave):
        task, data = super(MyMaster, self).get_data(completed_slave)
        return data


class MyApp(object):
    """
    This is my application that has a lot of work to do so it gives work to do
    to its slaves until all the work is done. There different type of work so
    the slaves must be able to do different tasks.
    Also want to limit the number of slaves reserved to one or more tasks. We
    make use of the MultiWorkQueue class that handles multiple Masters and where
    each Master can have an optional limits on the number of slaves.
    MultiWorkQueue moves slaves between Masters when some of them are idles and
    gives slaves back when the Masters have work again.
    """

    def __init__(self, slaves,  task1_num_slave=None, task2_num_slave=None):
        """
        Each task/master can be limited on the number of slaves by the init
        arguments. Leave them None if you don't want to limit a specific Master
        """
        #
        # create a Master for each task
        #
        self.master1 = MyMaster(task=Tasks.TASK1)
        self.master2 = MyMaster(task=Tasks.TASK2)

        #
        # MultiWorkQueue is a convenient class that run multiple work queues
        # Each task needs a Tuple  with (someID, Master, None or max slaves)
        #
        masters_details = [(Tasks.TASK1, self.master1, task1_num_slave),
                           (Tasks.TASK2, self.master2, task2_num_slave) ]
        self.work_queue = MultiWorkQueue(slaves, masters_details)


    def terminate_slaves(self):
        """
        Call this to make all slaves exit their run loop
        """
        self.master1.terminate_slaves()
        self.master2.terminate_slaves()

    def __add_next_task(self, i, task=None):
        """
        Create random tasks 1-3 and add it to the right work queue
        """
        if task is None:
            task = random.randint(1,2)

        if task == 1:
            args = i
            self.work_queue.add_work(Tasks.TASK1, args)
        elif task == 2:
            args = (i, i*2)
            self.work_queue.add_work(Tasks.TASK2, args)

    def run(self, min_buffer_tasks, len_window=800):
        """
        This is the core of my application, keep starting slaves
        as long as there is work to do
        """
        timestart = time.time()
        #
        # let's prepare our work queue. This can be built at initialization time
        # but it can also be added later as more work become available
        #
        #for i in range(tasks):
        #    self.__add_next_task(i)

        # Read your DataFrame
        ref_df, fastq_df, maf_df = read_from_folder("data")
        
        paf_row = 0
        paf_not_empty = True
        
        args = (paf_row, min_buffer_tasks)
        self.work_queue.insert_work(Tasks.TASK1, args)
        #
        # Keeep starting slaves as long as there is work to do
        #
        while not self.work_queue.done():

            #
            # give more work to do to each idle slave (if any)
            #
            self.work_queue.do_work()                
            #
            # reclaim returned data from completed slaves
            #
            for data in self.work_queue.get_completed_work(Tasks.TASK1):
                done, arg1 = data
                if done:
                    paf_df, paf_row = arg1  
                    paf_not_empty = not paf_df.empty
                    if paf_not_empty:
                        for i, (target, overlapping_df) in enumerate(paf_df.groupby("q_seq_name")):
                            target_sequence = fastq_df[target]
                            
                            subfastq_df = {key: fastq_df[key] for key in overlapping_df["t_seq_name"]}
                            
                            args = ((target, target_sequence, overlapping_df, len_window, subfastq_df), target)
                            self.work_queue.add_work(Tasks.TASK2, args)
                    print('Master: slave finished his task returning: %d)' % paf_row)
                    
                    args = (paf_row, min_buffer_tasks)
                    self.work_queue.insert_work(Tasks.TASK1, args)

            for data in self.work_queue.get_completed_work(Tasks.TASK2):
                done, arg1 = data
                if done:
                    target, consensus_sequence = arg1 
                    print('Master: slave finished his task : %s)' % target)
                    #with open("output.fastq", "a") as myfile:
                    #    myfile.write(f">{target}\n{consensus_sequence}\n")


            # sleep some time
            time.sleep(0.3)
        timeend = time.time()
        print(timeend - timestart)
            


class MySlave(Slave):
    """
    A slave process extends Slave class, overrides the 'do_work' method
    and calls 'Slave.run'. The Master will do the rest

    In this example we have different tasks but instead of creating a Slave for
    each type of taks we create only one class that can handle any type of work.
    This avoids having idle processes if, at certain times of the execution, there
    is only a particular type of work to do but the Master doesn't have the right
    slave for that task.
    """

    def __init__(self):
        super(MySlave, self).__init__()

    def do_work(self, args):
        
        # the data contains the task type
        task, data = args

        rank = MPI.COMM_WORLD.Get_rank()
        name = MPI.Get_processor_name()

        #
        # Every task type has its specific data input and return output
        #
        ret = None
        if task == Tasks.TASK1:

            paf_row, tasks = data
            paf_df, paf_row = read_dist_paf("data/overlap.paf", skiprows=paf_row, group_col_idx=0, n_process=tasks)
            #print('  Slave %s rank %d executing %s with task_id %d' % (name, rank, task, arg1) )
            ret = (True, (paf_df, paf_row))

        elif task == Tasks.TASK2:

            data, i = data
            target = data[0]
            # print(f"CREO FINESTRE {rank}")
            windows = process_target(*data)
            # print(windows)
            # print(f"CREO GRAFO {rank}")
            #for k, v in windows.items():
            consensus_sequence = process_windows(windows)
            
            print('  Slave %s rank %d executing %s with task_id %s' % (name, rank, task, target) )
            ret = (True, (target, consensus_sequence))

        return (task, ret)


def main():

    name = MPI.Get_processor_name()
    rank = MPI.COMM_WORLD.Get_rank()
    size = MPI.COMM_WORLD.Get_size()

    print('I am  %s rank %d (total %d)' % (name, rank, size) )

    if rank == 0: # Master
        task1_num_slave = 1
        task2_num_slave = size - 1 - task1_num_slave
        app = MyApp(slaves=range(1, size), task1_num_slave=task1_num_slave, task2_num_slave=task2_num_slave)
        app.run(min_buffer_tasks=task2_num_slave)
        app.terminate_slaves()

    else: # Any slave

        MySlave().run()

    print('Task completed (rank %d)' % (rank) )

if __name__ == "__main__":
    main()

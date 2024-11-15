from mpi4py import MPI
from mpi_master_slave import Master, Slave
from mpi_master_slave import WorkQueue
import time

from src.io import read_fasta, read_fastq, read_maf, read_from_folder, read_paf
from src.utils.lpt import lpt_scheduling
from src.processes import process_target
from src.processes import process_windows
from src.utils.split import split_dict_into_chunks

class MyApp(object):
    """
    This is my application that has a lot of work to do so it gives work to do
    to its slaves until all the work is done
    """

    def __init__(self, slaves):
        # when creating the Master we tell it what slaves it can handle
        self.master = Master(slaves)
        # WorkQueue is a convenient class that run slaves on a tasks queue
        self.work_queue = WorkQueue(self.master)

    def terminate_slaves(self):
        """
        Call this to make all slaves exit their run loop
        """
        self.master.terminate_slaves()

    def run(self, len_window=800):
        """
        This is the core of my application, keep starting slaves
        as long as there is work to do
        """
        #
        # let's prepare our work queue. This can be built at initialization time
        # but it can also be added later as more work become available
        #
        
        # Read your DataFrame
        ref_df, fastq_df, maf_df = read_from_folder("data")
        paf_df = read_paf("data/overlap.paf")
        
        #for i in range(tasks):
        #    # 'data' will be passed to the slave and can be anything
        #    self.work_queue.add_work(data=('Do task', i))
        for i, (target, overlapping_df) in enumerate(paf_df.groupby("q_seq_name")):
            target_sequence = fastq_df[target]
            self.work_queue.add_work(data=((target, target_sequence, overlapping_df, len_window, fastq_df), i))

       
        #
        # Keeep starting slaves as long as there is work to do
        #
        slave_times = []
        while not self.work_queue.done():

            #
            # give more work to do to each idle slave (if any)
            #
            self.work_queue.do_work()

            #
            # reclaim returned data from completed slaves
            #
            for slave_return_data in self.work_queue.get_completed_work():
                done, message, slave_time = slave_return_data
                slave_times.append(slave_time)
                if done:
                    print('Master: slave finished is task and says "%s"' % message)

            # sleep some time
            time.sleep(0.3)
    
        with open('ex1_slave_times.txt', 'w') as f:
            for line in slave_times:
                f.write(f"{line}\n")


class MySlave(Slave):
    """
    A slave process extends Slave class, overrides the 'do_work' method
    and calls 'Slave.run'. The Master will do the rest
    """

    def __init__(self):
        super(MySlave, self).__init__()

    def do_work(self, data):
        start_time = time.time()

        rank = MPI.COMM_WORLD.Get_rank()
        name = MPI.Get_processor_name()
        task, task_arg = data
        #print("DATA:", task[0])
        #print(f"CREO FINESTRE {rank}")
        windows = process_target(*task)
        #print(windows)
        #print(f"CREO GRAFO {rank}")
        consensus_sequence = process_windows(windows)
        end_time = time.time()

        
        
        return (True, 'I completed my task (%d)' % task_arg, end_time - start_time)


def main():

    name = MPI.Get_processor_name()
    rank = MPI.COMM_WORLD.Get_rank()
    size = MPI.COMM_WORLD.Get_size()

    print('I am  %s rank %d (total %d)' % (name, rank, size) )

    if rank == 0: # Master

        app = MyApp(slaves=range(1, size))
        app.run()
        app.terminate_slaves()

    else: # Any slave

        MySlave().run()

    print('Task completed (rank %d)' % (rank) )

if __name__ == "__main__":
    main()

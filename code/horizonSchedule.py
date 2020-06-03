import numpy as np 

class LinearSchedule(object):
    """
    expand time horizon linearly
    """

    def __init__(self, t_start=0.1, t_end=0.5, num_iters=20):
        self.T = t_start
        self.t_start = t_start
        self.t_end = t_end
        self.num_iters = num_iters

    def update(self, i, brs_step=0.05):
        """
        i: iteration
        brs_step: default time step size when solving BRS set through HelperOC
        """
        
        if i < self.num_iters:            
            self.T = self.t_start + float(i/self.num_iters)*(self.t_end - self.t_start)
        else:
            self.T = self.t_end
        print("Linear Scheduler Iteration: {} T = {:.2f}, real T = {:.2f}".format(i, self.T, int(self.T/brs_step)*brs_step))

if __name__ == "__main__":
    sch = LinearSchedule()
    for i in range(21):
        sch.update(i)

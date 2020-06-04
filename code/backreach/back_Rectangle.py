import matlab.engine
import os
import numpy as np
from scipy.interpolate import RectBivariateSpline, interp1d

X_IDX = 0
VX_IDX = 1
Y_IDX = 2
VY_IDX = 3
PHI_IDX = 4
W_IDX = 5

T1_IDX = 0
T2_IDX = 1

N = 20.

class Quad6DbackRectangle:

    def __init__(self):
        self.stateDims = 6
        self.actual_boundary = None
        self.center = None
        self.update_step = None

    def reset_variables(self, problem, plot_dir,
                        tMax=0.1, nPoints=251.):

        self.sampled_points = None
        self.actual_boundary = None
        self.most_recent_rectangle = None

        self.problem = problem
        self.plot_dir = plot_dir

        self.wRange = np.array([self.problem.state_space.low[W_IDX], self.problem.state_space.high[W_IDX]]);
        self.vxRange = np.array([self.problem.state_space.low[VX_IDX], self.problem.state_space.high[VX_IDX]]);
        self.vyRange = np.array([self.problem.state_space.low[VY_IDX], self.problem.state_space.high[VY_IDX]]);

        self.T1Min = self.T2Min = float(self.problem.env.unwrapped.Tmin)
        self.T1Max = self.T2Max = float(self.problem.env.unwrapped.Tmax)
        self.tMax = tMax

        x_low, vx_low, y_low, vy_low, phi_low, w_low = self.problem.state_space.low;
        self.stateMin = np.array([x_low, vx_low, y_low, vy_low, phi_low, w_low]);

        x_high, vx_high, y_high, vy_high, phi_high, w_high = self.problem.state_space.high;
        self.stateMax = np.array([x_high, vx_high, y_high, vy_high, phi_high, w_high]);

        self.nPoints = nPoints
        self.stateN = self.nPoints * np.ones((self.problem.state_dims, 1))   # not sure about the use


        ###################### MAYBE JUST FOR MATLAB ##############################

        ## debug
        print(self.problem.state_dims, nPoints)
        for i in range(self.problem.state_dims):
            print(self.stateMin[i], self.stateMax[i])
        # self.axis_coords = [np.linspace(self.stateMin[i][0], self.stateMax[i][0], int(nPoints)) for i in
        #                     range(self.problem.state_dims)]

        xg_lower = self.problem.env.unwrapped.xg_lower
        yg_lower = self.problem.env.unwrapped.yg_lower
        xg_upper = self.problem.env.unwrapped.xg_upper
        yg_upper = self.problem.env.unwrapped.yg_upper
        goal_w = self.problem.env.unwrapped.goal_w
        goal_vx = self.problem.env.unwrapped.goal_vx
        goal_vy = self.problem.env.unwrapped.goal_vy
        goal_phi = self.problem.env.unwrapped.goal_phi

        vRadius = self.problem.env.unwrapped.g_vel_limit
        phiRadius = self.problem.env.unwrapped.g_phi_limit
        posRadius = self.problem.env.unwrapped.g_pos_radius

        self.center = np.array([(xg_lower+xg_upper)/2., goal_vx, (yg_lower+yg_upper)/2., goal_vy, goal_phi, goal_w])

        self.goalRectAndState = np.array([xg_lower, yg_lower, xg_upper, yg_upper, goal_w, goal_vx, goal_vy, goal_phi])

        self.goalRadii = np.array([posRadius, vRadius, posRadius, vRadius, phiRadius, vRadius])

        self.update_step = (self.stateMax - self.stateMin)/N

        self.actual_boundary = np.zeros((2,self.stateMin.shape[0]))
        self.actual_boundary[0] = self.center
        self.actual_boundary[1] = self.center

        self.update_boundary()


        ###################### MAYBE JUST FOR MATLAB ##############################

    def set_goal(self, goal):
        self.center = goal

    def set_update_step(self,update_step):
        self.update_step = update_step


    def update_boundary(self, delta_t=0.1):
        self.actual_boundary[1] += delta_t * self.update_step
        self.actual_boundary[1] = np.minimum(self.actual_boundary[0], self.stateMax)  # the high boundary
        self.actual_boudaary[0] -= delta_t * self.update_step
        self.actual_boundary[0] = np.maximum(self.actual_boundary[1], self.stateMin)  # the low boundary


    def check_membership(self,points):
        inbound = np.logical_and(points<self.actual_boundary[1],points>self.actual_boundary[0])
        inbound = inbound.all(axis=1)

        not_collision = np.zeros_like(points[:, 0]).astype(bool)
        for idx in range(points.shape[0]):
            not_collision[idx] = not self.problem.env.unwrapped._in_obst(points[idx])

        return np.logical_and(not_collision,inbound)

    def evaluate_value_function(self,potential_samples):
        return np.sum(np.abs((potential_samples-self.center)/(self.stateMax-self.stateMin)), axis=1, keepdims=True)


    def sample_from_backrec(self,size=1, method='uniform'):
        print('sample_from_backRec, method =', method, flush=True)
        if method == 'uniform':

            num_successfully_sampled = 0
            successful_samples = list()
            while num_successfully_sampled < size:
                print('sample_from_backRec while loop', flush=True)

                potential_samples = np.random.uniform(low=self.actual_boundary[0], high=self.actual_boundary[1],
                                                      size=(size, self.problem.state_dims))
                membership = self.check_membership(potential_samples)
                member_samples = potential_samples[membership == True]
                num_sampled = member_samples.shape[0]
                if num_sampled == 0:
                    continue

                num_successfully_sampled += num_sampled
                successful_samples.append(member_samples)

            self.sampled_points = np.concatenate(successful_samples)
            print('sample_from_backRec done', flush=True)
            return self.sampled_points

        elif method == 'contour_edges':
            # Start by sampling 5x the points from a 20% larger box
            pct_added = 0.20
            sample_boundary = np.zeros((2, self.problem.state_dims))
            sample_boundary[0] = np.maximum(self.problem.state_space.low,
                                                 self.actual_boundary[0] - pct_added * np.abs(self.actual_boundary[0]))
            sample_boundary[1] = np.minimum(self.problem.state_space.high,
                                                 self.actual_boundary[1] + pct_added * np.abs(self.actual_boundary[1]))

            print("sample_boundary")
            print(sample_boundary)
            print("actual_bounds")
            print(self.actual_boundary)
            potential_samples = np.random.uniform(low=sample_boundary[0],
                                                  high=sample_boundary[1],
                                                  size=(size * 5, self.problem.state_dims))

            not_collision = np.zeros_like(potential_samples[:, 0]).astype(bool)
            for idx in range(potential_samples.shape[0]):
                not_collision[idx] = not self.problem.env.unwrapped._in_obst(potential_samples[idx])
            potential_samples = potential_samples[not_collision == True]

            # Then, evaluate their sampling weights
            weights = np.abs(self.evaluate_value_function(potential_samples))
            weights = np.reciprocal(weights)
            weights /= np.sum(weights)

            sampled_idxs = np.random.choice(potential_samples.shape[0],
                                            size=size,
                                            p=weights)

            self.sampled_points = potential_samples[sampled_idxs]
            print('sample_from_backRec done', flush=True)
            return self.sampled_points

        else:
            raise ValueError('Unknown backRec sampling method:', method)

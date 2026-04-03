

from legged_gym.envs.base.legged_robot_config import LeggedRobotCfg, LeggedRobotCfgPPO

class M2RoughCfg( LeggedRobotCfg ):
    class init_state( LeggedRobotCfg.init_state ):
        pos = [0.0, 0.0, 0.42] # x,y,z [m]
        default_joint_angles = { # = target angles [rad] when action = 0.0
            'FL_hip_joint': 0.0,   # [rad]
            'RL_hip_joint': 0.0,   # [rad]
            'FR_hip_joint': 0.0 ,  # [rad]
            'RR_hip_joint': 0.0,   # [rad]

            'FL_thigh_joint': -0.8,     # [rad]
            'RL_thigh_joint': -0.8,   # [rad]
            'FR_thigh_joint': -0.8,     # [rad]
            'RR_thigh_joint': -0.8,   # [rad]

            'FL_calf_joint': 1.5,   # [rad]
            'RL_calf_joint': 1.5,    # [rad]
            'FR_calf_joint': 1.5,  # [rad]
            'RR_calf_joint': 1.5,    # [rad]
        }

    class control( LeggedRobotCfg.control ):
        # PD Drive parameters:
        control_type = 'P'
        stiffness = {'joint': 25.0}  # [N*m/rad]
        damping = {'joint': 0.5}     # [N*m*s/rad]
        # action scale: target angle = actionScale * action + defaultAngle
        action_scale = 0.25
        # decimation: Number of control action updates @ sim DT per policy DT
        decimation = 4
        hip_reduction = 1.0

    class commands( LeggedRobotCfg.commands ):
            curriculum = True
            max_curriculum = 2.0
            num_commands = 4 # default: lin_vel_x, lin_vel_y, ang_vel_yaw, heading (in heading mode ang_vel_yaw is recomputed from heading error)
            resampling_time = 10. # time before command are changed[s]
            heading_command = True # if true: compute ang vel command from heading error
            class ranges( LeggedRobotCfg.commands.ranges):
                lin_vel_x = [-1.0, 1.0] # min max [m/s]
                lin_vel_y = [-1.0, 1.0]   # min max [m/s]
                ang_vel_yaw = [-3.14, 3.14]    # min max [rad/s]
                #ang_vel_yaw = [0, 0]    # min max [rad/s]
                heading = [-3.14, 3.14]

    class asset( LeggedRobotCfg.asset ):
        file = '{LEGGED_GYM_ROOT_DIR}/resources/robots/m2/urdf/m2.urdf'
        name = "m2"
        foot_name = "foot"
        penalize_contacts_on = ["thigh", "calf", "base"]
        terminate_after_contacts_on = ["base"]
        privileged_contacts_on = ["base", "thigh", "calf"]
        self_collisions = 1 # 1 to disable, 0 to enable...bitwise filter
        flip_visual_attachments = False # Some .obj meshes must be flipped from y-up to z-up

    class terrain( LeggedRobotCfg.terrain ):
        mesh_type = 'plane' # "heightfield" # none, plane, heightfield or trimesh
        horizontal_scale = 0.1 # [m]
        vertical_scale = 0.005 # [m]
        border_size = 25 # [m]
        curriculum = True
        static_friction = 1.0
        dynamic_friction = 1.0
        restitution = 0.
        # rough terrain only:
        measure_heights = True
        measured_points_x = [-0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8] # 1mx1.6m rectangle (without center line)
        measured_points_y = [-0.5, -0.4, -0.3, -0.2, -0.1, 0., 0.1, 0.2, 0.3, 0.4, 0.5]
        selected = False # select a unique terrain type and pass all arguments
        terrain_kwargs = None # Dict of arguments for selected terrain
        max_init_terrain_level = 5 # starting curriculum state
        terrain_length = 8.
        terrain_width = 8.
        num_rows= 10 # number of terrain rows (levels)
        num_cols = 20 # number of terrain cols (types)
        # terrain types: [smooth slope, rough slope, stairs up, stairs down, discrete]
        terrain_proportions = [0.1, 0.2, 0.3, 0.3, 0.1]
        # trimesh only:
        slope_treshold = 0.75 # slopes above this threshold will be corrected to vertical surfaces
  
    class rewards( LeggedRobotCfg.rewards ):
        class scales:
            termination = -0.0
            tracking_lin_vel = 2.0
            tracking_ang_vel = 1.0
            lin_vel_z = -2.0
            ang_vel_xy = -0.05
            orientation = -2.0
            dof_acc = -2.5e-7
            # joint_power = -2e-5
            base_height = -10.0
            # foot_clearance = -0.01
            action_rate = -0.01
            smoothness = -0.01
            feet_air_time =  1.0
            collision = -1.0
            feet_stumble = -0.0
            stand_still = -0.5
            torques = -0.0
            dof_vel = -0.0
            dof_pos_limits = -0.0
            dof_vel_limits = -0.0
            torque_limits = -0.0

            foot_clearance_up = -0.5
            foot_mirror_up = -1.0
            foot_slide_up = -0.1

        only_positive_rewards = False # if true negative total rewards are clipped at zero (avoids early termination problems)
        tracking_sigma = 0.25 # tracking reward = exp(-error^2/sigma)
        soft_dof_pos_limit = 1. # percentage of urdf limits, values above this limit are penalized
        soft_dof_vel_limit = 1.
        soft_torque_limit = 1.
        base_height_target = 0.3
        max_contact_force = 100. # forces above this value are penalized
        clearance_height_target = -0.18

    class domain_rand( LeggedRobotCfg.domain_rand ):
        randomize_payload_mass = True
        payload_mass_range = [-1, 2]

        randomize_com_displacement = True
        com_displacement_range = [-0.05, 0.05]

        randomize_link_mass = True
        link_mass_range = [0.9, 1.1]
        
        randomize_friction = True
        friction_range = [0.2, 1.25]
        
        randomize_restitution = True
        restitution_range = [0., 1.0]
        
        randomize_motor_strength = True
        motor_strength_range = [0.9, 1.1]
        
        randomize_kp = True
        kp_range = [0.8, 1.2]
        
        randomize_kd = True
        kd_range = [0.8, 1.2]
        
        randomize_initial_joint_pos = True
        initial_joint_pos_range = [0.5, 1.5]
        
        disturbance = True
        disturbance_range = [-30.0, 30.0]
        disturbance_interval = 8
        
        push_robots = True
        push_interval_s = 10
        max_push_vel_xy = 1.5

        delay = True

class M2RoughCfgPPO( LeggedRobotCfgPPO ):
    class algorithm( LeggedRobotCfgPPO.algorithm ):
        entropy_coef = 0.01
    class runner( LeggedRobotCfgPPO.runner ):
        run_name = ''
        experiment_name = 'rough_m2'

        num_steps_per_env = 100 
        max_iterations = 5000 
        save_interval = 100 

        #resume = True
        #resume_path = "/root/gpufree-data/HIMLoco/legged_gym/logs/rough_m2/Apr03_12-28-32_/model_1000.pt"

  
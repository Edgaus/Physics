import numpy as np
from scipy.interpolate import interp1d
import itertools

class Grider:
    def __init__(self, x_array, type_of_grid, meshes=None):  
        self.meshes = np.asarray(meshes) # Aseguramos que soporte listas
        self.x_axis = np.asarray(x_array)
        self.grid_type = type_of_grid

        self.bounds = np.insert( self.x_axis.cumsum( ),0,0  )
        self.x_grid = None
        self.dx = None

############################## Code for x_grid ###################################        

    def grid_axis(self):
        
        x_grid = []
        dx = []
        number_points = 0
        
        if self.grid_type == 'constant':
            start, end, step =  self.bounds[0], self.bounds[-1], self.meshes[0] 
            num_points = int(  round(end/step)   ) 
            
            x_grid = np.linspace( start+step, end, num_points)           
            dx = np.full(num_points, step)


        elif self.grid_type == 'uniform':
            
            for i in range(len(self.meshes)):    

                start, end, step =  self.bounds[i], self.bounds[i+1], self.meshes[i] 
                num_points_i = int(  round((end-start)/step)   )

                layer_points = np.linspace(start + step, end, num_points_i)
                
                x_grid.append(layer_points)
                dx.append(  np.full(num_points_i, step) )

            x_grid = np.concatenate(x_grid)
            dx = np.concatenate(dx)

        elif self.grid_type == 'variable':
            current = 0
            
            for count, step in self.meshes:
                start = current
                end = start + (count * step)
                
                # Use linspace to generate the exact chunk, skipping the start point
                chunk_points = np.linspace( start + step, end, int(count))
                x_grid.append(chunk_points)
                
                # Update current for the next chunk
                current = end
                
            # Glue the grid together
            x_grid = np.concatenate(x_grid)
            
            # Use the efficient repeat trick to generate the dx array instantly
            counts = np.array(self.meshes)[:, 0].astype(int)
            steps = np.array(self.meshes)[:, 1]
            dx = np.repeat(steps, counts)

        self.x_grid = x_grid
        self.dx = dx
        return x_grid, dx


############################# Library ####################################

    def meshes_library(self, mesh_example = 'fine'):

        if mesh_example == 'fine':
            # [count, step]
            mesh_array = [ 
    # --- Left Barrier ( 360 Å Total) ---
                [3, 32.0],   # 96 Å (Deep in the barrier, low probability)
                [5, 16.0],   # 80 Å
                [8, 8.0],    # 64 Å
                [12, 4.0],   # 48 Å
                [16, 2.0],   # 32 Å
                [20, 1.0],   # 20 Å
                [20, 0.5],   # 10 Å
                [100, 0.1],   # 5 Å (Right before the interface, high curvature)

    # --- Quantum Well (56 Å Total) ---
                [560, 0.1],  # 56 Å (Ultra-high precision inside the well!)

    # --- Right Barrier ( 360 Å Total) ---
                [100, 0.1],   # 5 Å (Right after the interface)
                [20, 0.5],   # 10 Å
                [20, 1.0],   # 20 Å
                [16, 2.0],   # 32 Å
                [12, 4.0],   # 48 Å
                [8, 8.0],    # 64 Å
                [5, 16.0],   # 80 Å
                [3, 32.0]    # 96 Å (Deep in the right barrier)
                ]
        return mesh_array



############################## Function of Properties ###################################  


    def Heaviside(self, x_eval):
        y_eval = np.zeros_like( x_eval )
        for i in range( len( self.propertie ) ):
            mask =  self.propertie[i] * (np.heaviside(  x_eval - self.bounds[i], 0.5 ) -   np.heaviside( x_eval - self.bounds[i+1]  , 0.5 )     )  
            y_eval += mask 
        y_eval[-1] = y_eval[-1]*2
        return y_eval

    
    def inf_sheet_potential(self, x_eval):
        e_0 = 8.85e-12
        e = 1.609e-19
        e_medium = 12.9

        sigma = e*(  (  (200)*1E18* 1E6*1E-20  )  /  ( 2*e_medium*e_0)   )   
        start_layer = 400

        y_eval = np.abs( x_eval - start_layer )*( sigma )
        return y_eval 
    
    def spontanuos_field_bwb(self,x_eval):  #Calculate the case of Barrier/Well/Barrier potential

        


        # Left Barrier: active from bounds[0] to bounds[1]
        left_barrier = np.heaviside(x_eval - self.bounds[0], 0.5) - np.heaviside(x_eval - self.bounds[1], 0.5)
        
        # Central Well: active from bounds[1] to bounds[2]
        well = np.heaviside(x_eval - self.bounds[1], 0.5) - np.heaviside(x_eval - self.bounds[2], 0.5)
        
        # Right Barrier: active from bounds[2] to bounds[3]
        right_barrier = np.heaviside(x_eval - self.bounds[2], 0.5) - np.heaviside(x_eval - self.bounds[3], 0.5)
        
        # Total Field F(x)
        F = self.F_b * (left_barrier + right_barrier) + self.F_w * well

        return F
             
        

############################## Code for propertie_grid ###################################  


    def grid_propertie( self, propertie_array = None, type_propertie = 'step', constants_properties = None  ):

        self.type_propertie = type_propertie
        self.propertie = np.asarray(propertie_array)
        self.constants_properties = np.asanyarray(constants_properties)

        if self.x_grid is None or self.dx is None:
            x, h = self.grid_axis()
        else:
            x = self.x_grid
           
     
        if self.type_propertie == 'step':
            y = self.Heaviside(x)
            return y
            
        if self.type_propertie == 'inf_sheet_potential':
            y = self.inf_sheet_potential(x) 
            return y
        
        if self.type_propertie == 'inf_sheet_potential':
            y = self.inf_sheet_potential(x) 
            return y
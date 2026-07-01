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
    
############################## Funciones utiles extras

    def vegard(self, Initial, Final, x, bowing=0):
        return (1 - x) * Initial + x * Final - bowing * x * (1 - x)


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

        vacum_permitivty = 8.85E-12 # F/C

        Psp_AlN = -0.081  #  C/m2
        Psp_GaN = -0.029  #  C/m2
        Psp_InN = -0.032 # C/m2

        ############# AlN ###############

        #Parametro de Red
        a_AlN = 3.112E-10 #m

        #Constantes elasticas
        C13_AlN = 99 #+- 4GPa
        C33_AlN = 398 # +-10GPa

        #Constantes pizoelectricas
        e31_AlN = -0.58 # Cm-2
        e33_AlN = 1.55 # Cm-2
        dielectric_AlN = 8.5 

        ############# GaN ###############

        a_GaN = 3.189E-10 #m
         #Constantes elasticas
        C13_GaN = 106 #+- 20GPa 
        C33_GaN = 398 #+- 20GPa

        #Constantes pizoelectricas
        e31_GaN = -0.33 # Cm-2
        e33_GaN = 0.65 # Cm-2      
        dielectric_GaN = 8.9     

        ############# InN ###############

        a_InN = 3.533E-10 #m
         #Constantes elasticas
        C13_InN = 121 #+- 7GPa 
        C33_InN = 182 #+- 6GPa

        #Constantes pizoelectricas
        e31_InN = -0.57 # Cm-2
        e33_InN = 0.97 # Cm-2      
        dielectric_InN = 15.3 

        ############################### AlGaN ######################

        x_Al = 0.3

        a_AlGaN = self.vegard( a_GaN, a_AlN, x_Al  ) #m
         #Constantes elasticas
        C13_AlGaN = self.vegard( C13_GaN, C13_AlN, x_Al  ) #+- 7GPa 
        C33_AlGaN = self.vegard( C33_GaN, C33_AlN, x_Al  )#+- 6GPa

        #Constantes pizoelectricas
        e31_AlGaN = self.vegard( e31_GaN, e31_AlN, x_Al  ) # Cm-2
        e33_AlGaN = self.vegard( e33_GaN, e33_AlN, x_Al  ) # Cm-2    
        
        Psp_AlGaN = self.vegard( Psp_GaN, Psp_AlN, x_Al )


        ############################### AlInN ######################

        x_In = 0.2

        a_AlInN = self.vegard( a_AlN, a_InN, x_In  ) #m
         #Constantes elasticas
        C13_AlInN = self.vegard( C13_AlN, C13_InN, x_In  ) #+- 7GPa 
        C33_AlInN = self.vegard( C33_AlN, C33_InN, x_In  )#+- 6GPa

        #Constantes pizoelectricas
        e31_AlInN = self.vegard( e31_AlN, e31_InN, x_In  ) # Cm-2
        e33_AlInN = self.vegard( e33_AlN, e33_InN, x_In  ) # Cm-2

        Psp_AlInN = self.vegard( Psp_AlN, Psp_InN, x_In )    

        # La densidad de carga per sheet viene dado al final como


        a_barrier = a_AlGaN
        a_well = a_GaN 

        C13_well = C13_GaN
        C33_well = C33_GaN

        e31_well = e31_GaN
        e33_well = e33_GaN

        Psp_well = Psp_AlGaN
        Psp_barrier = Psp_GaN

        strain = (a_barrier - a_well)/a_well

        sigma = abs(               
            2*strain* (   e31_well -  e33_well*( C13_well  / C33_well )      ) + Psp_well - Psp_barrier
             )


        Electric_field = sigma/(vacum_permitivty*dielectric_AlN)
        print( Electric_field )


        lw = 20E-10
        lb = 40E-10
        epsilon = vacum_permitivty*dielectric_AlN
        
        strain_biaxial = ( a_AlGaN-a_GaN  )/a_AlGaN

        Pw = 2*strain_biaxial*(  e31_GaN - e33_GaN*( C13_GaN/C33_GaN  )      )

        print(Pw)


        Pb = 2*strain_biaxial*(  e31_GaN - e33_GaN*( C13_GaN/C33_GaN  )      )

        Fb = (Pw-Pb)*lw/(vacum_permitivty*epsilon*(lw+lb))
        Fw = 2*(Pb-Pw)*lb/(vacum_permitivty*epsilon*(lw+lb))




        # Left Barrier: active from bounds[0] to bounds[1]
        left_barrier = np.heaviside(x_eval - self.bounds[0], 0.5) - np.heaviside(x_eval - self.bounds[1], 0.5)
        
        # Central Well: active from bounds[1] to bounds[2]
        well = np.heaviside(x_eval - self.bounds[1], 0.5) - np.heaviside(x_eval - self.bounds[2], 0.5)
        
        # Right Barrier: active from bounds[2] to bounds[3]
        right_barrier = np.heaviside(x_eval - self.bounds[2], 0.5) - np.heaviside(x_eval - self.bounds[3], 0.5)
        
        # Total Field F(x)
        F_z = left_barrier*Fb*x_eval +  well * (Fb*self.bounds[1] + Fw * x_eval) + right_barrier* (Fb*self.bounds[1] + Fw * self.bounds[2] + Fb * x_eval)

        return F_z



    def analytical_band_profile_zeroed(self,x_eval):

        lw = 100.0       
        Vb = 1.54       
        Fw = -3.90 * 0.01 
        Fb = 0.334 * 0.01 

        # Bandgaps 
        Eg_pozo = 4.0    
        Eg_barrera = 6.2 
        
        def E_conduccion(z):
            if z < 0:
                return Fb * z + Vb
            elif 0 <= z <= lw:
                return Fw * z
            else:
                return Fb * (z - lw) + Fw * lw + Vb

        def Bandgap(z):
            if 0 <= z <= lw:
                return Eg_pozo
            else:
                return Eg_barrera

        def E_valencia(z):
            return E_conduccion(z) - Bandgap(z)

        Ec_vec = np.vectorize(E_conduccion)
        Ev_vec = np.vectorize(E_valencia)

        
        return Ec_vec(x_eval-250), Ev_vec(x_eval-250)
        



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
        
        if self.type_propertie == 'analytical_band_profile_zeroed':
            y = self.analytical_band_profile_zeroed(x) 
            return y
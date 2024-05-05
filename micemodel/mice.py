import numpy as np
from reshaper import Reshaper
import utils

class Model:
    def __init__(self):
        self.bodies = {"female": Reshaper(label="female"), "male":Reshaper(label="male")}
        self.body = self.bodies["female"]
        self.flag_ = 0

        self.vertices = self.body.mean_vertex
        self.normals = self.body.normals
        self.facets = self.body.facets
        self.input_data = np.zeros((utils.M_NUM, 1))

    
    def update(self):
        [self.vertices, self.normals, self.facets] = \
            self.body.mapping(self.input_data, self.flag_)
        self.vertices = self.vertices.astype('float32')

    def save(self):
        utils.save_obj("/home/mahdy/Desktop/Backup/Application/Thesis-Flutter-Frontend/assets/meshes/result.obj", self.vertices, self.facets+1)

    def predict(self,data):
        # print("-----------------predict---------------------")
        # print(data)
        mask = np.zeros((utils.M_NUM, 1), dtype=bool)
        for i in range(0, data.shape[0]):
            if data[i, 0] != 0:
                data[i, 0] -= self.body.mean_measure[i, 0]
                data[i, 0] /= self.body.std_measure[i, 0]
                mask[i, 0] = 1

        # print("-----------------before predict input---------------------")
        # print(self.input_data)

        # print("-----------------before predict data---------------------")
        # print(data)
        
        # print("-----------------mask---------------------")
        # print(mask)

        self.input_data = self.body.get_predict(mask, data)
        # print("-----------------after predict input---------------------")
        # print(self.input_data)
        # print("-----------------after predict data---------------------")
        # print(data)
        # print("-----------------mask---------------------")
        # print(mask)

        self.update()

    def generate_object_file(self, weight, height, hips = 0, chest = 0, waist = 0, gender = "female" ):
        self.body = self.bodies[gender]
        data = []
        for i in range(0, utils.M_NUM):
            data.append(0)
        data[0] = (weight ** (1.0 / 3.0) * 1000)
        data[1] = (height * 10)
        data[3] = chest * 10
        data[10] = waist * 10
        data[11] = hips * 10

        data = np.array(data).reshape(utils.M_NUM, 1)
        self.predict(data)

        file = open("dump/body_model.obj", 'w')
        v = self.vertices
        f = self.facets + 1
        for i in range(0, v.shape[0]):
            file.write('v %f %f %f\n'%(v[i][0], v[i][1], v[i][2]))
        for i in range(0, f.shape[0]):
            file.write('f %d %d %d\n'%(f[i][0], f[i][1], f[i][2]))
     
        return file

        #return self.save()
        #return self.save()
        #return the generated file  


if __name__ == "__main__":
    model = Model()
    model.generate_object_file(72,178,94,82,94,"male")
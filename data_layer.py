# written by longriyao

"""
    The data_layer is provide data to the net
"""
import caffe
import cv2
import yaml
import os
import numpy as np
import random
from batch import get_batch
class DataLayer(caffe.Layer):

    _current = 0
    
    def _get_next_batch_paths(self):
        if self._current + self._batch_size >= len(self._image_paths):
            batch = self._image_paths[self._current:]
            
            more = self._batch_size - (len(self._image_paths) - self._current)
            batch.extend(self._image_paths[0:more])
            self._current = more
        else:
            batch = self._image_paths[self._current:(self._current + self._batch_size)]
            self._current += self._batch_size
        return batch
    
    def _get_next_batch(self):

        next_batch_paths = self._get_next_batch_paths()
        #batch_data_path = [self._image_paths[i] for i in indexs]
        return get_batch(next_batch_paths)
    
    def _get_param(self):
        # parse 
        layer_params = yaml.load(self.param_str_)
        # get the param
        if layer_params.has_key('batch_size'):
            self._batch_size = layer_params['batch_size']
        else:
            self._batch_size = 32

        if layer_params.has_key('root_folder'):
            self._root_folder = layer_params['root_folder']
        else:
            self._root_folder = ""

        if layer_params.has_key('source'):
            self._source = layer_params['source']
        else:
            print "must write the source field in data_layer"
            assert 0
        if layer_params.has_key('height'):
            self._height = layer_params['height']
        else:
            self._height = 64

        if layer_params.has_key('weight'):
            self._weight = layer_params['weight']
        else:
            self._weight = 64
        if layer_params.has_key('shuffle'):
            self._shuffle = layer_params['shuffle']
        else:
            self._shuffle = True
            
    def _get_data_path(self):    
        file = open(self._source,'r')
        self._image_paths = file.readlines()
        
        if self._shuffle:
            random.shuffle(self._image_paths)
        # add folder 
        if self._root_folder:
            for i in xrange(len(self._image_paths)):
                self._image_paths[i] = os.path.join(self._root_folder,self._image_paths[i])
                
    def setup(self,bottom,top):
        # setup function

        #map name to top index
        self._blob_name_to_index = {}
        # get param 
        self._get_param()
        # get data path from param 
        self._get_data_path()
        # reshape top 
        top[0].reshape(self._batch_size, 1, self._height, self._weight)
        self._blob_name_to_index["gray_image"] = 0

        top[1].reshape(self._batch_size_, 3, self._height, self._weight)
        self._blob_name_to_index["color_image"] = 1
        if len(top) == 3:
            self._blob_name_to_index["label"] = 2
            top[2].reshape(self._batch_size_,1)

    def forward(self,bottom,top):

        blobs = self._get_next_batch()

        for blob_name, blob in blobs.iteritems():
            top_index = self._blob_name_to_index[blob_name]
            #copy data to top
            top[top_index].data[...] = blob.astype(np.float32,copy=False)

    def backward(self, top, propagate_down, bottom):
        pass

    def reshape(self, bottom, top):
        pass

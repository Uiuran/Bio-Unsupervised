# -*- coding: utf-8 -*-
"""Tensorboard.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FZtbHbqpDHCimmEKpjK8e89UrT-DW066

#Tensorboard
"""

import tensorflow as TF
#from keras.callbacks import ModelCheckpoint, LearningRateScheduler, TensorBoard as Board, EarlyStopping
import numpy as np

# Tensorboard display
from IPython.display import clear_output, Image, display, HTML

from keras import applications

sess = TF.Session()
model = applications.VGG19(weights = "imagenet", include_top=False, input_shape = (2050, 2050, 3))

"""Escreve definição de grafo de computação do modelo em .pb através da Sessão."""

# função util para congelar partes do grafo de computação e deletá-las ou move-las para outro arquivo
#  TF.compat.v1.graph_util.convert_variables_to_constants?

graph = sess.graph.as_graph_def()
TF.train.write_graph(graph, "model", "./TF_model.pb", as_text=False)

"""Importando definição do grafo de computação do modelo gerado pela API Keras"""

model_fn = '/content/model/TF_model.pb'

# creating TensorFlow session and loading the model
graph = TF.Graph()
sess = TF.InteractiveSession(graph=graph)
with TF.gfile.FastGFile(model_fn, 'rb') as f:
    graph_def = TF.GraphDef()
    graph_def.ParseFromString(f.read())
t_input = TF.placeholder(np.float32, name='input') # define the input tensor
imagenet_mean = 117.0
t_preprocessed = TF.expand_dims(t_input-imagenet_mean, 0)
TF.import_graph_def(graph_def)

"""Visualização do grafo de computação com Tensorboard no notebook"""

# funções auxiliares
def strip_consts(graph_def, max_const_size=32):
    """Strip large constant values from graph_def."""
    strip_def = TF.GraphDef()
    for n0 in graph_def.node:
        n = strip_def.node.add() 
        n.MergeFrom(n0)
        if n.op == 'Const':
            tensor = n.attr['value'].tensor
            size = len(tensor.tensor_content)
            if size > max_const_size:
                tensor.tensor_content = TF.compat.as_bytes("<stripped %d bytes>"%size)
    return strip_def
  
def rename_nodes(graph_def, rename_func):
    res_def = TF.GraphDef()
    for n0 in graph_def.node:
        n = res_def.node.add() 
        n.MergeFrom(n0)
        n.name = rename_func(n.name)
        for i, s in enumerate(n.input):
            n.input[i] = rename_func(s) if s[0]!='^' else '^'+rename_func(s[1:])
    return res_def

# Função que usa HTML e javascript para exibir tensorboar no notebook e web
def show_graph(graph_def, max_const_size=32):
    """Visualize TensorFlow graph."""
    if hasattr(graph_def, 'as_graph_def'):
        graph_def = graph_def.as_graph_def()
    strip_def = strip_consts(graph_def, max_const_size=max_const_size)
    code = """
        <script>
          function load() {{
            document.getElementById("{id}").pbtxt = {data};
          }}
        </script>
        <link rel="import" href="https://tensorboard.appspot.com/tf-graph-basic.build.html" onload=load()>
        <div style="height:600px">
          <tf-graph-basic id="{id}"></tf-graph-basic>
        </div>
    """.format(data=repr(str(strip_def)), id='graph'+str(np.random.rand()))
  
    iframe = """
        <iframe seamless style="width:800px;height:620px;border:0" srcdoc="{}"></iframe>
    """.format(code.replace('"', '&quot;'))
    display(HTML(iframe))

show_graph(graph_def)

"""**TODO**: Tensorboard utilizando Keras durante o Fit

**Sites uteis para visualização**

#### Deep-dream visualizar canais de features

https://nbviewer.jupyter.org/github/tensorflow/tensorflow/blob/master/tensorflow/examples/tutorials/deepdream/deepdream.ipynb

#### Keras para .pb (TF graph definition)
  https://www.dlology.com/blog/how-to-convert-trained-keras-model-to-tensorflow-and-make-prediction/

#### Tensorboard guia
https://www.tensorflow.org/tensorboard/r1/summaries
"""
# Hybride model of SDAE and MF. One hidden layer is used in the SDAE.

import h5py
import numpy as np
import random
import auto_functions as auto

INPUT_LAYER = 314
HIDDEN_UNIT1 = 40
HIDDEN_UNIT2 = 40
LEARNING_RATE = 0.001 / 50
EPOCH_NUM = 50
mu, sigma = 0, 0.1
l = 40
alpha = 40
l2_u = 100.0
l2_v = 100.0
lambda_reg = 0.01  # مقدار L2 Regularization
batch = 500
ratio_l = 300.0
ratio_u = 1.0

def main(denoise=True):
    diction = [('ind_empleado', 5), ('pais_residencia', 24), ('sexo', 3), ('ind_nuevo', 2), ('indrel', 2), 
               ('indrel_1mes', 4), ('tiprel_1mes', 4), ('indresi', 2), ('indext', 2), ('conyuemp', 3), 
               ('canal_entrada', 158), ('indfall', 2), ('cod_prov', 53), ('ind_actividad_cliente', 2), 
               ('segmento', 4), ('antiguedad_binned', 10), ('age_binned', 24), ('renta_binned', 10)]
    lenList = [tup[1] for tup in diction]
    accList = [sum(lenList[:i+1]) for i in range(len(lenList))]
    
    with h5py.File('user_infor.h5', 'r') as hf:
        xtrain = hf['infor'][:]
    with h5py.File('rating_tr_numpy.h5', 'r') as hf:
        rating_mat = hf['rating'][:]
    
    W1, b1, c1 = auto.initialization(INPUT_LAYER, [HIDDEN_UNIT1], mu, sigma)
    u = np.random.rand(rating_mat.shape[0], l)
    v = np.random.rand(rating_mat.shape[1], l)

    # Define preference and confidence matrices
    p = np.zeros(rating_mat.shape)
    p[rating_mat > 0] = 1
    c = 1 + alpha * rating_mat

    iteration = 30

    print('Start training...')
    for iterate in range(iteration):
        # Update u
        for i in range(rating_mat.shape[0]):
            c_diag = np.diag(c[i, :])
            temp_u = np.dot(np.dot(p[i, :], c_diag), v)
            u[i, :] = np.dot(temp_u, np.linalg.pinv(l2_u * np.identity(l) + np.dot(np.dot(v.T, c_diag), v) + lambda_reg * u[i, :]))
        print('u update complete')

        # Update v
        for j in range(rating_mat.shape[1]):
            c_diag = np.diag(c[:, j])
            temp_v = np.dot(np.dot(p[:, j], c_diag), u)
            v[j, :] = np.dot(temp_v, np.linalg.pinv(l2_v * np.identity(l) + np.dot(np.dot(u.T, c_diag), u) + lambda_reg * v[j, :]))
        print('v update complete')
        print('Loss:', np.linalg.norm(p - np.dot(u, v.T)))

        # Run the autoencoder function to update weights
        W1, b1, c1 = auto.autoEncoder_mono(ratio_l, ratio_u, batch, W1, xtrain, u, b1, c1, accList, EPOCH_NUM, LEARNING_RATE, denoise=True)
        hidden = auto.getoutPut_mono(W1, b1, xtrain, accList)
        u = hidden
        print('Updated loss after autoencoder:', np.linalg.norm(p - np.dot(u, v.T)))

    # Save updated matrices
    with h5py.File('u_40_mono_40+100_auto.h5', 'w') as hf:
        hf.create_dataset("u", data=u)
    with h5py.File('v_40_mono_40+100_auto.h5', 'w') as hf:
        hf.create_dataset("v", data=v)
    with h5py.File('W1_40_mono_40+100.h5', 'w') as hf:
        hf.create_dataset("W1", data=W1)
    with h5py.File('b1_40_mono_40+100.h5', 'w') as hf:
        hf.create_dataset("b1", data=b1)
    with h5py.File('c1_40_mono_40+100.h5', 'w') as hf:
        hf.create_dataset("c1", data=c1)

    return hidden

main(denoise=True)

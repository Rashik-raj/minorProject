from .attention import AttentionLayer
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
from keras.preprocessing.text import Tokenizer 
from keras.preprocessing.sequence import pad_sequences
from keras import backend as K
import tensorflow as tf
from tensorflow.keras.layers import Input, LSTM, Embedding, Dense, Concatenate, TimeDistributed
from tensorflow.keras.models import Model
from .preprocessing import text_cleaner, convertSequence, getData
import numpy as np
import pandas as pd
global graph
#load data
x_tr,x_val,y_tr,y_val = getData()
max_text_len=30
max_summary_len=8
#prepare a tokenizer for reviews on training data
x_tokenizer = Tokenizer() 
x_tokenizer.fit_on_texts(list(x_tr))
thresh=4
cnt=0
tot_cnt=0
freq=0
tot_freq=0
for key,value in x_tokenizer.word_counts.items():
    tot_cnt=tot_cnt+1
    tot_freq=tot_freq+value
    if(value<thresh):
        cnt=cnt+1
        freq=freq+value
#prepare a tokenizer for reviews on training data
x_tokenizer = Tokenizer(num_words=tot_cnt-cnt) 
x_tokenizer.fit_on_texts(list(x_tr))
#convert text sequences into integer sequences
x_tr_seq    =   x_tokenizer.texts_to_sequences(x_tr) 
x_val_seq   =   x_tokenizer.texts_to_sequences(x_val)
#padding zero upto maximum length
x_tr    =   pad_sequences(x_tr_seq,  maxlen=max_text_len, padding='post')
x_val   =   pad_sequences(x_val_seq, maxlen=max_text_len, padding='post')
#size of vocabulary ( +1 for padding token)
x_voc = x_tokenizer.num_words + 1

#prepare a tokenizer for reviews on training data
y_tokenizer = Tokenizer()   
y_tokenizer.fit_on_texts(list(y_tr))
thresh=6
cnt=0
tot_cnt=0
freq=0
tot_freq=0
for key,value in y_tokenizer.word_counts.items():
    tot_cnt=tot_cnt+1
    tot_freq=tot_freq+value
    if(value<thresh):
        cnt=cnt+1
        freq=freq+value
y_tokenizer = Tokenizer(num_words=tot_cnt-cnt) 
y_tokenizer.fit_on_texts(list(y_tr))
#convert text sequences into integer sequences
y_tr_seq    =   y_tokenizer.texts_to_sequences(y_tr) 
y_val_seq   =   y_tokenizer.texts_to_sequences(y_val)
#padding zero upto maximum length
y_tr    =   pad_sequences(y_tr_seq, maxlen=max_summary_len, padding='post')
y_val   =   pad_sequences(y_val_seq, maxlen=max_summary_len, padding='post')
#size of vocabulary
y_voc  =   y_tokenizer.num_words + 1
#delete that only start and end
ind=[]
for i in range(len(y_tr)):
    cnt=0
    for j in y_tr[i]:
        if j!=0:
            cnt=cnt+1
    if(cnt==2):
        ind.append(i)

y_tr=np.delete(y_tr,ind, axis=0)
x_tr=np.delete(x_tr,ind, axis=0)
ind=[]
for i in range(len(y_val)):
    cnt=0
    for j in y_val[i]:
        if j!=0:
            cnt=cnt+1
    if(cnt==2):
        ind.append(i)

y_val=np.delete(y_val,ind, axis=0)
x_val=np.delete(x_val,ind, axis=0)

latent_dim = 300
embedding_dim=100
tf.compat.v1.Session()
# Encoder
encoder_inputs = Input(shape=(max_text_len,))
#embedding layer
enc_emb =  Embedding(x_voc, embedding_dim,trainable=True)(encoder_inputs)
#encoder lstm 1
encoder_lstm1 = LSTM(latent_dim,return_sequences=True,return_state=True,dropout=0.4,recurrent_dropout=0.4)
encoder_output1, state_h1, state_c1 = encoder_lstm1(enc_emb)
#encoder lstm 2
encoder_lstm2 = LSTM(latent_dim,return_sequences=True,return_state=True,dropout=0.4,recurrent_dropout=0.4)
encoder_output2, state_h2, state_c2 = encoder_lstm2(encoder_output1)
#encoder lstm 3
encoder_lstm3=LSTM(latent_dim, return_state=True, return_sequences=True,dropout=0.4,recurrent_dropout=0.4)
encoder_outputs, state_h, state_c= encoder_lstm3(encoder_output2)
# Set up the decoder, using `encoder_states` as initial state.
decoder_inputs = Input(shape=(None,))
#embedding layer
dec_emb_layer = Embedding(y_voc, embedding_dim,trainable=True)
dec_emb = dec_emb_layer(decoder_inputs)
decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True,dropout=0.4,recurrent_dropout=0.2)
decoder_outputs,decoder_fwd_state, decoder_back_state = decoder_lstm(dec_emb,initial_state=[state_h, state_c])
# Attention layer
attn_layer = AttentionLayer(name='attention_layer')
attn_out, attn_states = attn_layer([encoder_outputs, decoder_outputs])
# Concat attention input and decoder LSTM output
decoder_concat_input = Concatenate(axis=-1, name='concat_layer')([decoder_outputs, attn_out])
#dense layer
decoder_dense =  TimeDistributed(Dense(y_voc, activation='softmax'))
decoder_outputs = decoder_dense(decoder_concat_input)

# Define/load the model the model
model = Model([encoder_inputs, decoder_inputs], decoder_outputs)
model.compile(optimizer='rmsprop', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
#model.fit([x_tr,y_tr[:,:-1]], y_tr.reshape(y_tr.shape[0],y_tr.shape[1], 1)[:,1:] ,epochs=50,callbacks=[es],batch_size=128, validation_data=([x_val,y_val[:,:-1]], y_val.reshape(y_val.shape[0],y_val.shape[1], 1)[:,1:]))
model.load_weights('home/trainedModel_weights3.h5')
graph = tf.compat.v1.get_default_graph()

reverse_target_word_index=y_tokenizer.index_word
reverse_source_word_index=x_tokenizer.index_word
target_word_index=y_tokenizer.word_index

def decode_sequence(input_seq):
    with graph.as_default():
        encoder_inputs = Input(shape=(max_text_len,))
        #embedding layer
        enc_emb =  Embedding(x_voc, embedding_dim,trainable=True)(encoder_inputs)
        #encoder lstm 1
        encoder_lstm1 = LSTM(latent_dim,return_sequences=True,return_state=True,dropout=0.4,recurrent_dropout=0.4)
        encoder_output1, state_h1, state_c1 = encoder_lstm1(enc_emb)
        #encoder lstm 2
        encoder_lstm2 = LSTM(latent_dim,return_sequences=True,return_state=True,dropout=0.4,recurrent_dropout=0.4)
        encoder_output2, state_h2, state_c2 = encoder_lstm2(encoder_output1)
        #encoder lstm 3
        encoder_lstm3=LSTM(latent_dim, return_state=True, return_sequences=True,dropout=0.4,recurrent_dropout=0.4)
        encoder_outputs, state_h, state_c= encoder_lstm3(encoder_output2)
        # Set up the decoder, using `encoder_states` as initial state.
        decoder_inputs = Input(shape=(None,))
        #embedding layer
        dec_emb_layer = Embedding(y_voc, embedding_dim,trainable=True)
        dec_emb = dec_emb_layer(decoder_inputs)
        decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True,dropout=0.4,recurrent_dropout=0.2)
        decoder_outputs,decoder_fwd_state, decoder_back_state = decoder_lstm(dec_emb,initial_state=[state_h, state_c])
        # Attention layer
        attn_layer = AttentionLayer(name='attention_layer')
        attn_out, attn_states = attn_layer([encoder_outputs, decoder_outputs])
        # Concat attention input and decoder LSTM output
        decoder_concat_input = Concatenate(axis=-1, name='concat_layer')([decoder_outputs, attn_out])
        #dense layer
        decoder_dense =  TimeDistributed(Dense(y_voc, activation='softmax'))
        decoder_outputs = decoder_dense(decoder_concat_input)
        model = Model([encoder_inputs, decoder_inputs], decoder_outputs)
        model.compile(optimizer='rmsprop', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        model.load_weights('home/trainedModel_weights3.h5')
        ########### inferencing ###########
        encoder_model = Model(inputs=encoder_inputs,outputs=[encoder_outputs, state_h, state_c])
        # Decoder setup, Below tensors will hold the states of the previous time step
        decoder_state_input_h = Input(shape=(latent_dim,))
        decoder_state_input_c = Input(shape=(latent_dim,))
        decoder_hidden_state_input = Input(shape=(max_text_len,latent_dim))
        # Get the embeddings of the decoder sequence
        dec_emb2= dec_emb_layer(decoder_inputs) 
        # To predict the next word in the sequence, set the initial states to the states from the previous time step
        decoder_outputs2, state_h2, state_c2 = decoder_lstm(dec_emb2, initial_state=[decoder_state_input_h, decoder_state_input_c])
        #attention inference
        attn_out_inf, attn_states_inf = attn_layer([decoder_hidden_state_input, decoder_outputs2])
        decoder_inf_concat = Concatenate(axis=-1, name='concat')([decoder_outputs2, attn_out_inf])
        # A dense softmax layer to generate prob dist. over the target vocabulary
        decoder_outputs2 = decoder_dense(decoder_inf_concat)
        # Final decoder model
        decoder_model = Model(
            [decoder_inputs] + [decoder_hidden_state_input,decoder_state_input_h, decoder_state_input_c],
            [decoder_outputs2] + [state_h2, state_c2])
        ##############inferencing end ###############
        e_out, e_h, e_c = encoder_model.predict(input_seq)    
        # Generate empty target sequence of length 1.
        target_seq = np.zeros((1,1))    
        # Populate the first word of target sequence with the start word.
        target_seq[0, 0] = target_word_index['sostok']
        stop_condition = False
        decoded_sentence = ''
        while not stop_condition:
            output_tokens, h, c = decoder_model.predict([target_seq] + [e_out, e_h, e_c])
            # Sample a token
            sampled_token_index = np.argmax(output_tokens[0, -1, :])
            sampled_token = reverse_target_word_index[sampled_token_index]        
            if(sampled_token!='eostok'):
                decoded_sentence += ' '+sampled_token
            # Exit condition: either hit max length or find stop word.
            if (sampled_token == 'eostok'  or len(decoded_sentence.split()) >= (max_summary_len-1)):
                stop_condition = True
            # Update the target sequence (of length 1).
            target_seq = np.zeros((1,1))
            target_seq[0, 0] = sampled_token_index
            # Update internal states
            e_h, e_c = h, c
    return decoded_sentence

def getSummary(data): 
    x_pred = [text_cleaner(data,0)]
    x_pred = convertSequence(x_pred,x_tokenizer)
    return decode_sequence(x_pred.reshape(1,30))

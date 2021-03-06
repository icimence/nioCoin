from pprint import pprint
from ltp import LTP
import tensorflow as tf
import numpy as np
import time
import datetime
import os
import network
from sklearn.metrics import average_precision_score

FLAGS = tf.app.flags.FLAGS


# embedding the position
def pos_embed(x):
    if x < -60:
        return 0
    if -60 <= x <= 60:
        return x + 61
    if x > 60:
        return 122


def main_for_evaluation():
    pathname = "./model/ATT_GRU_model-"

    wordembedding = np.load('./data/vec.npy')

    test_settings = network.Settings()
    test_settings.vocab_size = 16693
    test_settings.num_classes = 12
    test_settings.big_num = 5561

    big_num_test = test_settings.big_num

    with tf.Graph().as_default():

        sess = tf.Session()
        with sess.as_default():

            def test_step(word_batch, pos1_batch, pos2_batch, y_batch):

                feed_dict = {}
                total_shape = []
                total_num = 0
                total_word = []
                total_pos1 = []
                total_pos2 = []

                for i in range(len(word_batch)):
                    total_shape.append(total_num)
                    total_num += len(word_batch[i])
                    for word in word_batch[i]:
                        total_word.append(word)
                    for pos1 in pos1_batch[i]:
                        total_pos1.append(pos1)
                    for pos2 in pos2_batch[i]:
                        total_pos2.append(pos2)

                total_shape.append(total_num)
                total_shape = np.array(total_shape)
                total_word = np.array(total_word)
                total_pos1 = np.array(total_pos1)
                total_pos2 = np.array(total_pos2)

                feed_dict[mtest.total_shape] = total_shape
                feed_dict[mtest.input_word] = total_word
                feed_dict[mtest.input_pos1] = total_pos1
                feed_dict[mtest.input_pos2] = total_pos2
                feed_dict[mtest.input_y] = y_batch

                loss, accuracy, prob = sess.run(
                    [mtest.loss, mtest.accuracy, mtest.prob], feed_dict)
                return prob, accuracy

            with tf.variable_scope("model"):
                mtest = network.GRU(is_training=False, word_embeddings=wordembedding, settings=test_settings)

            names_to_vars = {v.op.name: v for v in tf.global_variables()}
            saver = tf.train.Saver(names_to_vars)

            # testlist = range(1000, 1800, 100)
            testlist = [9000]

            for model_iter in testlist:
                # for compatibility purposes only, name key changes from tf 0.x to 1.x, compat_layer
                saver.restore(sess, pathname + str(model_iter))

                time_str = datetime.datetime.now().isoformat()
                print(time_str)
                print('Evaluating all test data and save data for PR curve')

                test_y = np.load('./data/testall_y.npy')
                test_word = np.load('./data/testall_word.npy')
                test_pos1 = np.load('./data/testall_pos1.npy')
                test_pos2 = np.load('./data/testall_pos2.npy')
                allprob = []
                acc = []
                for i in range(int(len(test_word) / float(test_settings.big_num))):
                    prob, accuracy = test_step(test_word[i * test_settings.big_num:(i + 1) * test_settings.big_num],
                                               test_pos1[i * test_settings.big_num:(i + 1) * test_settings.big_num],
                                               test_pos2[i * test_settings.big_num:(i + 1) * test_settings.big_num],
                                               test_y[i * test_settings.big_num:(i + 1) * test_settings.big_num])
                    acc.append(np.mean(np.reshape(np.array(accuracy), (test_settings.big_num))))
                    prob = np.reshape(np.array(prob), (test_settings.big_num, test_settings.num_classes))
                    for single_prob in prob:
                        allprob.append(single_prob[1:])
                allprob = np.reshape(np.array(allprob), (-1))
                order = np.argsort(-allprob)

                print('saving all test result...')
                current_step = model_iter

                np.save('./out/allprob_iter_' + str(current_step) + '.npy', allprob)
                allans = np.load('./data/allans.npy')

                # caculate the pr curve area
                average_precision = average_precision_score(allans, allprob)
                print('PR curve area:' + str(average_precision))


def main(_):
    ltp = LTP()
    ltp.init_dict(path="../entity_dict.txt", max_window=4)
    # If you retrain the model, please remember to change the path to your own model below:
    pathname = "./model/nioCoin_ATT_GRU_model-1200"

    wordembedding = np.load('./data/vec.npy')
    test_settings = network.Settings()
    test_settings.vocab_size = 16693
    test_settings.num_classes = 12
    test_settings.big_num = 1

    with tf.Graph().as_default():
        sess = tf.Session()
        with sess.as_default():
            def test_step(word_batch, pos1_batch, pos2_batch, y_batch):

                feed_dict = {}
                total_shape = []
                total_num = 0
                total_word = []
                total_pos1 = []
                total_pos2 = []

                for i in range(len(word_batch)):
                    total_shape.append(total_num)
                    total_num += len(word_batch[i])
                    for word in word_batch[i]:
                        total_word.append(word)
                    for pos1 in pos1_batch[i]:
                        total_pos1.append(pos1)
                    for pos2 in pos2_batch[i]:
                        total_pos2.append(pos2)

                total_shape.append(total_num)
                total_shape = np.array(total_shape)
                total_word = np.array(total_word)
                total_pos1 = np.array(total_pos1)
                total_pos2 = np.array(total_pos2)

                feed_dict[mtest.total_shape] = total_shape
                feed_dict[mtest.input_word] = total_word
                feed_dict[mtest.input_pos1] = total_pos1
                feed_dict[mtest.input_pos2] = total_pos2
                feed_dict[mtest.input_y] = y_batch

                loss, accuracy, prob = sess.run(
                    [mtest.loss, mtest.accuracy, mtest.prob], feed_dict)
                return prob, accuracy

            with tf.variable_scope("model"):
                mtest = network.GRU(is_training=False, word_embeddings=wordembedding, settings=test_settings)

            names_to_vars = {v.op.name: v for v in tf.global_variables()}
            saver = tf.train.Saver(names_to_vars)
            saver.restore(sess, pathname)

            print('reading word embedding data...')
            vec = []
            word2id = {}
            f = open('./origin_data/vec.txt', encoding='utf-8')
            content = f.readline()
            content = content.strip().split()
            dim = int(content[1])
            while True:
                content = f.readline()
                if content == '':
                    break
                content = content.strip().split()
                word2id[content[0]] = len(word2id)
                content = content[1:]
                content = [(float)(i) for i in content]
                vec.append(content)
            f.close()
            word2id['UNK'] = len(word2id)
            word2id['BLANK'] = len(word2id)

            print('reading relation to id')
            relation2id = {}
            id2relation = {}
            f = open('./origin_data/relation2id.txt', 'r', encoding='utf-8')
            while True:
                content = f.readline()
                if content == '':
                    break
                content = content.strip().split()
                relation2id[content[0]] = int(content[1])
                id2relation[int(content[1])] = content[0]
            f.close()

            file = open('../??????????????????????????????.txt', encoding='utf-8')
            line = file.readline()
            entity_list = []
            relation_list = []
            entity_file = open('../entity_dict.txt', encoding='utf-8')
            entity = entity_file.readline()
            while entity:
                if len(entity) > 0 and (entity != '\n' or entity != '\r' or entity != '\n\r'):
                    entity_list.append(entity.replace('\n', '').replace('\r', ''))
                entity = entity_file.readline()
            entity_file.close()
            print('entity_list:', entity_list)
            while line:
                # try:
                # BUG: Encoding error if user input directly from command line.
                if len(line) == 0 or line == '\n' or line == '\r' or line == '\n\r':
                    line = file.readline()
                    continue
                entity_find_list = []
                print('line:', line)
                segment, _ = ltp.seg([line])
                for seg_item in segment[0]:
                    if seg_item in entity_list and seg_item not in entity_find_list:
                        entity_find_list.append(seg_item)
                print('entity_find_list:', entity_find_list)
                sentence = line
                line = file.readline()
                if len(entity_find_list) > 1:
                    for k_1 in range(len(entity_find_list)):
                        for k_2 in range(k_1 + 1, len(entity_find_list)):
                            en1 = entity_find_list[k_1]
                            en2 = entity_find_list[k_2]
                            print("??????1: " + en1)
                            print("??????2: " + en2)
                            print(sentence)
                            relation = 0
                            en1pos = sentence.find(en1)
                            if en1pos == -1:
                                en1pos = 0
                            en2pos = sentence.find(en2)
                            if en2pos == -1:
                                en2post = 0
                            output = []
                            # length of sentence is 70
                            fixlen = 70
                            # max length of position embedding is 60 (-60~+60)
                            maxlen = 60

                            # Encoding test x
                            for i in range(fixlen):
                                word = word2id['BLANK']
                                rel_e1 = pos_embed(i - en1pos)
                                rel_e2 = pos_embed(i - en2pos)
                                output.append([word, rel_e1, rel_e2])

                            for i in range(min(fixlen, len(sentence))):

                                word = 0
                                if sentence[i] not in word2id:
                                    # print(sentence[i])
                                    # print('==')
                                    word = word2id['UNK']
                                    # print(word)
                                else:
                                    # print(sentence[i])
                                    # print('||')
                                    word = word2id[sentence[i]]
                                    # print(word)

                                output[i][0] = word
                            test_x = []
                            test_x.append([output])

                            # Encoding test y
                            label = [0 for i in range(len(relation2id))]
                            label[0] = 1
                            test_y = []
                            test_y.append(label)

                            test_x = np.array(test_x)
                            test_y = np.array(test_y)

                            test_word = []
                            test_pos1 = []
                            test_pos2 = []

                            for i in range(len(test_x)):
                                word = []
                                pos1 = []
                                pos2 = []
                                for j in test_x[i]:
                                    temp_word = []
                                    temp_pos1 = []
                                    temp_pos2 = []
                                    for k in j:
                                        temp_word.append(k[0])
                                        temp_pos1.append(k[1])
                                        temp_pos2.append(k[2])
                                    word.append(temp_word)
                                    pos1.append(temp_pos1)
                                    pos2.append(temp_pos2)
                                test_word.append(word)
                                test_pos1.append(pos1)
                                test_pos2.append(pos2)

                            test_word = np.array(test_word)
                            test_pos1 = np.array(test_pos1)
                            test_pos2 = np.array(test_pos2)

                            # print("test_word Matrix:")
                            # print(test_word)
                            # print("test_pos1 Matrix:")
                            # print(test_pos1)
                            # print("test_pos2 Matrix:")
                            # print(test_pos2)

                            prob, accuracy = test_step(test_word, test_pos1, test_pos2, test_y)
                            prob = np.reshape(np.array(prob), (1, test_settings.num_classes))[0]
                            print("?????????:")
                            # print(prob)
                            top3_id = prob.argsort()[-3:][::-1]
                            for n, rel_id in enumerate(top3_id):
                                print("No." + str(n + 1) + ": " + id2relation[rel_id] + ", Probability is " + str(prob[rel_id]))
                                relation_list.append([en1, en2, str(prob[rel_id]), id2relation[rel_id]])
                        # except Exception as e:
                        #    print(e)

                        # result = model.evaluate_line(sess, input_from_line(line, char_to_id), id_to_tag)
                        # print(result)
            print(relation_list)


if __name__ == "__main__":
    tf.app.run()

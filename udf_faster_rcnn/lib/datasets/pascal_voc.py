# --------------------------------------------------------
# Deformable Convolutional Networks
# Copyright (c) 2017 Microsoft
# Licensed under The Apache-2.0 License [see LICENSE for details]
# Modified by Shuo Wang
# --------------------------------------------------------

"""
Pascal VOC database
This class loads ground truth notations from standard Pascal VOC XML data formats
and transform them into IMDB format. Selective search is used for proposals, see roidb
function. Results are written as the Pascal VOC format. Evaluation is based on mAP
criterion.
"""

import pickle
import cv2
import os
import numpy as np
import PIL
from .imdb import imdb
from .imdb import ROOT_DIR
from . import ds_utils
from .voc_eval import voc_eval



class UADETRAC(imdb):
    def __init__(self, image_set, root_path, devkit_path=None, result_path=None, mask_size=-1, binary_thresh=None):
        """
        fill basic information to initialize imdb
        :param image_set: 2007_trainval, 2007_test, etc
        :param root_path: 'selective_search_data' and 'cache'
        :param devkit_path: data and results
        :return: imdb object
        """
        self.year = 2017
        # year = image_set.split('_')[0]
        # image_set = image_set[len(year) + 1 : len(image_set)]
        super(UADETRAC, self).__init__('UADETRAC')  # set self.name
        #self._img_ext='.jpg'
        self._img_ext = '.ppm'

        # self.year = year
        self.root_path = root_path
        #self.devkit_path = devkit_path
        self._devkit_path = self._get_default_path() if devkit_path is None \
            else devkit_path
        #print(devkit_path)
        self.ann_path="/home/pballapuram3/Eva/faster_rcnn_pytorch/data/VOCdevkit2007/VOC2007/Red_Annotations/gt.txt"
        self.ind_box_present=[]
        with open(self.ann_path,'r') as f:
            lines=f.readlines()
            for line in lines:
                self.ind_box_present.append(line.split(";")[0])
        self.ind_box_present=list(set(self.ind_box_present))

        self.data_path = "/home/pballapuram3/Eva/faster_rcnn_pytorch/data/VOCdevkit2007/VOC2007/Red_Data"

        #self._classes = ('__background__',  # always index 0
        #                'car','bus','van','others')
        self._classes = ('__background__','sign')
        self._num_classes = len(self.classes)
        #self.image_set_index = os.listdir(self.data_path + '/Annotations')
        self.image_set_index = os.listdir(self.data_path)
        self.image_set_index=sorted(self.image_set_index)
        print(len(self.image_set_index))
        #self._num_images = len(self.image_set_index)
        #print('num_images', self._num_images)
        self.mask_size = mask_size
        self.binary_thresh = binary_thresh

        self.config = {'comp_id': 'comp4',
                       'use_diff': False,
                       'min_size': 2}

    def load_image_set_index(self):
        """
        find out which indexes correspond to given image set (train or val)
        :return:
        """
        image_set_index_file = os.path.join(self.data_path, 'Sequences', self.image_set + '.txt')
        assert os.path.exists(image_set_index_file), 'Path does not exist: {}'.format(image_set_index_file)
        with open(image_set_index_file) as f:
            image_set_index = [x.strip() for x in f.readlines()]
        return image_set_index

    def _get_default_path(self):
        """
        Return the default path where PASCAL VOC is expected to be installed.
        """
        return os.path.join("/home/pballapuram3/Eva/faster_rcnn_pytorch/data/", 'VOCdevkit2007')

    def image_path_from_index(self, index):
        """
        given image index, find out full path
        :param index: index of a specific image
        :return: full path of this image
        """
        #print(index)
        image_path = os.path.join(self.data_path,index)
        #image_path = os.path.join(self.data_path, 'Insight-MVT_Annotation_Train',
        #                          index[:-4])
        assert os.path.exists(image_path), \
            'Path does not exist: {}'.format(image_path)
        return image_path

    def image_id_at(self, i):
        """
        Return the absolute path to image i in the image sequence.
        """
        return i

    def segmentation_path_from_index(self, index):
        """
        given image index, find out the full path of segmentation class
        :param index: index of a specific image
        :return: full path of segmentation class
        """
        seg_class_file = os.path.join(self.data_path, 'SegmentationClass', index + '.png')
        assert os.path.exists(seg_class_file), 'Path does not exist: {}'.format(seg_class_file)
        return seg_class_file

    def gt_roidb(self):
        """
        return ground truth image regions database
        :return: imdb[image_index]['boxes', 'gt_classes', 'gt_overlaps', 'flipped']
        """
        cache_file = os.path.join(self.cache_path, self.name + '_gt_roidb.pkl')
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as fid:
                roidb = pickle.load(fid)
            print('{} gt roidb loaded from {}'.format(self.name, cache_file))
            return roidb

        # gt_roidb = [self.load_UADETRAC_annotation(index) for index in self.image_set_index]
        gt_roidb = []
        #ind=self.ind_box_present[np.random.randint(0,len(self.ind_box_present),1)[0]]
        #print("Chosen " +str(ind))
        for index in self.image_set_index[:700]:
        #   gt_roidb.extend(self.load_UADETRAC_annotation(index))
            gt_roidb.extend(self.load_red_annotation(index))
        #with open(cache_file, 'wb') as fid:
        #    pickle.dump(gt_roidb, fid, pickle.HIGHEST_PROTOCOL)
        #print('wrote gt roidb to {}'.format(cache_file))

        return gt_roidb

    def gt_roidb_Shuo(self):
        """
        return ground truth image regions database
        :return: imdb[image_index]['boxes', 'gt_classes', 'gt_overlaps', 'flipped']
        """
        cache_file = os.path.join(self.cache_path, self.name + '_gt_roidb.pkl')
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as fid:
                roidb = pickle.load(fid)
            print('{} gt roidb loaded from {}'.format(self.name, cache_file))
            return roidb

        # gt_roidb = [self.load_UADETRAC_annotation(index) for index in self.image_set_index]
        gt_roidb = []
        for index in self.image_set_index:
            gt_roidb.extend(self.load_UADETRAC_annotation_Shuo(index))

        with open(cache_file, 'wb') as fid:
            pickle.dump(gt_roidb, fid, pickle.HIGHEST_PROTOCOL)
        print('wrote gt roidb to {}'.format(cache_file))

        return gt_roidb

    def gt_segdb(self):
        """
        return ground truth image regions database
        :return: imdb[image_index]['boxes', 'gt_classes', 'gt_overlaps', 'flipped']
        """
        cache_file = os.path.join(self.cache_path, self.name + '_gt_segdb.pkl')
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as fid:
                segdb = pickle.load(fid)
            print('{} gt segdb loaded from {}'.format(self.name, cache_file))
            return segdb

        gt_segdb = [self.load_pascal_segmentation_annotation(index) for index in self.image_set_index]
        with open(cache_file, 'wb') as fid:
            pickle.dump(gt_segdb, fid, pickle.HIGHEST_PROTOCOL)
        print('wrote gt segdb to {}'.format(cache_file))

        return gt_segdb

    def load_UADETRAC_annotation(self, index):
        """
        for a given sequence, load images and bounding boxes info from XML file
        :param index: index of a specific sequence
        :return: record['boxes', 'gt_classes', 'gt_overlaps', 'flipped']
        """
        import xml.etree.ElementTree as ET
        print("In Annotation")
        roi_recs = []
        #image_folder = self.image_path_from_index(index)
        print(index)
        filename = os.path.join(self.data_path, 'Annotations',  index)
        tree = ET.parse(filename)
        frames = tree.findall('frame')
        for ix, frame in enumerate(frames):
            density = frame.attrib['density']  # string '7'
            frame_num = frame.attrib['num']  # string '1'
            img_num = ''
            if len(frame_num) < 5:
                for iter_img_num in range(5 - len(frame_num)):
                    img_num = '0' + img_num
            img_num = img_num + frame_num

            roi_rec = dict()
            #print("Log!!!!!!")
            roi_rec['image'] = os.path.join(self.image_path_from_index(index), 'img' + img_num + '.jpg')

            # print(roi_rec['image'] )
            im_size = cv2.imread(roi_rec['image'], cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION).shape
            # print roi_rec['image'], im_size
            roi_rec['height'] = float(im_size[0])
            roi_rec['width'] = float(im_size[1])

            target_list = frame.findall('target_list')
            if len(target_list) > 0:
                tl = target_list[0]
                targets = tl.findall('target')

                # if not self.config['use_diff']:
                #    non_diff_objs = [obj for obj in objs if int(obj.find('difficult').text) == 0]
                #    objs = non_diff_objs
                num_targets = len(targets)

                boxes = np.zeros((num_targets, 4), dtype=np.uint16)
                gt_classes = np.zeros((num_targets), dtype=np.int32)
                overlaps = np.zeros((num_targets, self.num_classes), dtype=np.float32)

                class_to_index = dict(zip(self.classes, range(self.num_classes)))
                # Load object bounding boxes into a data frame.
                for ix, target in enumerate(targets):
                    bbox = target.find('box').attrib
                    gr_truth = target.find('attribute').attrib['vehicle_type']
                    # Make pixel indexes 0-based
                    x1 = float(bbox['left']) - 1
                    y1 = float(bbox['top']) - 1
                    x2 = x1 + float(bbox['width'])
                    y2 = y1 + float(bbox['height'])

                    # x1 = float(bbox.find('xmin').text) - 1
                    # y1 = float(bbox.find('ymin').text) - 1
                    # x2 = float(bbox.find('xmax').text) - 1
                    # y2 = float(bbox.find('ymax').text) - 1
                    # cls = class_to_index[obj.find('name').text.lower().strip()]
                    cls = class_to_index[gr_truth]
                    boxes[ix, :] = [x1, y1, x2, y2]
                    gt_classes[ix] = cls
                    overlaps[ix, cls] = 1.0

                    roi_rec.update({'boxes': boxes,
                                    'gt_classes': gt_classes,
                                    'gt_overlaps': overlaps,
                                    'max_classes': overlaps.argmax(axis=1),
                                    'max_overlaps': overlaps.max(axis=1),
                                    'flipped': False})
            roi_recs.append(roi_rec)
        return roi_recs

    def load_UADETRAC_annotation_Shuo(self, index):
        """
        for a given sequence, load images and bounding boxes info from XML file
        :param index: index of a specific sequence
        :return: record['boxes', 'gt_classes', 'gt_overlaps', 'flipped']
        """
        import xml.etree.ElementTree as ET

        roi_recs = []
        image_folder = self.image_path_from_index(index)
        # filename = os.path.join(self.data_path, 'TrainSequences', index)
        # tree = ET.parse(filename)
        frames = os.listdir(image_folder)
        for ix, frame in enumerate(frames):
            roi_rec = dict()
            roi_rec['image'] = os.path.join(self.image_path_from_index(index), frame)
            # print(roi_rec['image'] )
            im_size = cv2.imread(roi_rec['image'], cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION).shape
            # print roi_rec['image'], im_size
            roi_rec['height'] = float(im_size[0])
            roi_rec['width'] = float(im_size[1])


            target_list = frame.findall('target_list')
            if len(target_list)>0:
                tl = target_list[0]
            targets = tl.findall('target')

         #if not self.config['use_diff']:
         #    non_diff_objs = [obj for obj in objs if int(obj.find('difficult').text) == 0]
         #    objs = non_diff_objs
            num_targets = len(targets)

            boxes = np.zeros((num_targets, 4), dtype=np.uint16)
            gt_classes = np.zeros((num_targets), dtype=np.int32)
            overlaps = np.zeros((num_targets, self.num_classes), dtype=np.float32)

            class_to_index = dict(zip(self.classes, range(self.num_classes)))
            # Load object bounding boxes into a data frame.
            for ix, target in enumerate(targets):
                bbox = target.find('box').attrib
                gr_truth=target.find('attribute').attrib['vehicle_type']
                # Make pixel indexes 0-based
                x1 = float(bbox['left'])-1
                y1 = float(bbox['top'])-1
                x2 = x1 + float(bbox['width'])
                y2 = y1 + float(bbox['height'])

                #x1 = float(bbox.find('xmin').text) - 1
                #y1 = float(bbox.find('ymin').text) - 1
                #x2 = float(bbox.find('xmax').text) - 1
                #y2 = float(bbox.find('ymax').text) - 1
                #cls = class_to_index[obj.find('name').text.lower().strip()]
                cls = class_to_index[gr_truth]
                boxes[ix, :] = [x1, y1, x2, y2]
                gt_classes[ix] = cls
                overlaps[ix, cls] = 1.0

            roi_rec.update({'boxes': boxes,
                         'gt_classes': gt_classes,
                         'gt_overlaps': overlaps,
                         'max_classes': overlaps.argmax(axis=1),
                         'max_overlaps': overlaps.max(axis=1),
                         'flipped': False})
            overlaps = np.ones((1, self.num_classes), dtype=np.float32)
            roi_rec.update({'boxes': np.zeros((1, 4), dtype=np.uint16),
                            'gt_classes': np.ones((1), dtype=np.int32),
                            'gt_overlaps': overlaps,
                            'max_classes': overlaps.argmax(axis=1),
                            'max_overlaps': overlaps.max(axis=1),
                            'flipped': False})
            roi_recs.append(roi_rec)
        return roi_recs

    def load_red_annotation(self, ind):
        """
        for a given sequence, load images and bounding boxes info from XML file
        :param index: index of a specific sequence
        :return: record['boxes', 'gt_classes', 'gt_overlaps', 'flipped']
        """

        roi_recs = []
        #for index in range(0,500):
        b = []
        index=ind
        roi_rec = dict()
        roi_rec['image'] = self.image_path_from_index(index)
        im_size = cv2.imread(roi_rec['image'], cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION).shape
        roi_rec['height'] = float(im_size[0])
        roi_rec['width'] = float(im_size[1])

        with open("/home/pballapuram3/Eva/faster_rcnn_pytorch/data/VOCdevkit2007/VOC2007/Red_Annotations/gt.txt",'r') as f:
            ann=f.readlines()
        cnt=-1
        for line in ann:
            f_name=line.split(';')[0]
            if index == f_name:
                b.append([])
                cnt+=1
                for j in range(1,5):
                    b[cnt].append(int(line.split(';')[j]))

        #if not self.config['use_diff']:
         #    non_diff_objs = [obj for obj in objs if int(obj.find('difficult').text) == 0]
         #    objs = non_diff_objs
        if len(b)>0:
            num_targets = cnt+1
            boxes = np.asarray(b,dtype=np.uint16)
            gt_classes = np.ones(num_targets, dtype=np.int32)
            overlaps = np.zeros((num_targets, self.num_classes), dtype=np.float32)
            overlaps[:,1]=1.0
            # Load object bounding boxes into a data frame.
            roi_rec.update({'boxes': boxes,
                         'gt_classes': gt_classes,
                         'gt_overlaps': overlaps,
                         'max_classes': overlaps.argmax(axis=1),
                         'max_overlaps': overlaps.max(axis=1),
                         'flipped': False})
            roi_recs.append(roi_rec)
        return roi_recs

    def load_selective_search_roidb(self, gt_roidb):
        """
        turn selective search proposals into selective search roidb
        :param gt_roidb: [image_index]['boxes', 'gt_classes', 'gt_overlaps', 'flipped']
        :return: roidb: [image_index]['boxes', 'gt_classes', 'gt_overlaps', 'flipped']
        """
        import scipy.io
        matfile = os.path.join(self.root_path, 'selective_search_data', self.name + '.mat')
        assert os.path.exists(matfile), 'selective search data does not exist: {}'.format(matfile)
        raw_data = scipy.io.loadmat(matfile)['boxes'].ravel()  # original was dict ['images', 'boxes']

        box_list = []
        for i in range(raw_data.shape[0]):
            boxes = raw_data[i][:, (1, 0, 3, 2)] - 1  # pascal voc dataset starts from 1.
            #keep = unique_boxes(boxes)
            #boxes = boxes[keep, :]
            #keep = filter_small_boxes(boxes, self.config['min_size'])
            #boxes = boxes[keep, :]
            box_list.append(boxes)

        return self.create_roidb_from_box_list(box_list, gt_roidb)

    def selective_search_roidb(self, gt_roidb, append_gt=False):
        """
        get selective search roidb and ground truth roidb
        :param gt_roidb: ground truth roidb
        :param append_gt: append ground truth
        :return: roidb of selective search
        """
        cache_file = os.path.join(self.cache_path, self.name + '_ss_roidb.pkl')
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as fid:
                roidb = pickle.load(fid)
            print
            '{} ss roidb loaded from {}'.format(self.name, cache_file)
            return roidb

        if append_gt:
            print('appending ground truth annotations')
            ss_roidb = self.load_selective_search_roidb(gt_roidb)
            roidb = imdb.merge_roidbs(gt_roidb, ss_roidb)
        else:
            roidb = self.load_selective_search_roidb(gt_roidb)
        with open(cache_file, 'wb') as fid:
            pickle.dump(roidb, fid, pickle.HIGHEST_PROTOCOL)
        print('wrote ss roidb to {}'.format(cache_file))

        return roidb

    def load_pascal_segmentation_annotation(self, index):
        """
        for a given index, load image and bounding boxes info from XML file
        :param index: index of a specific image
        :return: record['seg_cls_path', 'flipped']
        """
        import xml.etree.ElementTree as ET
        seg_rec = dict()
        seg_rec['image'] = self.image_path_from_index(index)
        size = cv2.imread(seg_rec['image']).shape
        seg_rec['height'] = size[0]
        seg_rec['width'] = size[1]

        seg_rec['seg_cls_path'] = self.segmentation_path_from_index(index)
        seg_rec['flipped'] = False

        return seg_rec

    def evaluate_detections(self, detections):
        """
        top level evaluations
        :param detections: result matrix, [bbox, confidence]
        :return: None
        """
        # make all these folders for results
        result_dir = os.path.join(self.result_path, 'results')
        if not os.path.exists(result_dir):
            os.mkdir(result_dir)
        year_folder = os.path.join(self.result_path, 'results', 'VOC' + self.year)
        if not os.path.exists(year_folder):
            os.mkdir(year_folder)
        res_file_folder = os.path.join(self.result_path, 'results', 'VOC' + self.year, 'Main')
        if not os.path.exists(res_file_folder):
            os.mkdir(res_file_folder)

        self.write_pascal_results(detections)
        info = self.do_python_eval()
        return info

    def evaluate_segmentations(self, pred_segmentations=None):
        """
        top level evaluations
        :param pred_segmentations: the pred segmentation result
        :return: the evaluation results
        """
        # make all these folders for results
        if not (pred_segmentations is None):
            self.write_pascal_segmentation_result(pred_segmentations)

        info = self._py_evaluate_segmentation()
        return info

    def write_pascal_segmentation_result(self, pred_segmentations):
        """
        Write pred segmentation to res_file_folder
        :param pred_segmentations: the pred segmentation results
        :param res_file_folder: the saving folder
        :return: [None]
        """
        result_dir = os.path.join(self.result_path, 'results')
        if not os.path.exists(result_dir):
            os.mkdir(result_dir)
        year_folder = os.path.join(self.result_path, 'results', 'VOC' + self.year)
        if not os.path.exists(year_folder):
            os.mkdir(year_folder)
        res_file_folder = os.path.join(self.result_path, 'results', 'VOC' + self.year, 'Segmentation')
        if not os.path.exists(res_file_folder):
            os.mkdir(res_file_folder)

        result_dir = os.path.join(self.result_path, 'results', 'VOC' + self.year, 'Segmentation')
        if not os.path.exists(result_dir):
            os.mkdir(result_dir)

        pallete = self.get_pallete(256)

        for i, index in enumerate(self.image_set_index):
            segmentation_result = np.uint8(np.squeeze(np.copy(pred_segmentations[i])))
            segmentation_result = PIL.Image.fromarray(segmentation_result)
            segmentation_result.putpalette(pallete)
            segmentation_result.save(os.path.join(result_dir, '%s.png' % (index)))

    def get_pallete(self, num_cls):
        """
        this function is to get the colormap for visualizing the segmentation mask
        :param num_cls: the number of visulized class
        :return: the pallete
        """
        n = num_cls
        pallete = [0] * (n * 3)
        for j in range(0, n):
            lab = j
            pallete[j * 3 + 0] = 0
            pallete[j * 3 + 1] = 0
            pallete[j * 3 + 2] = 0
            i = 0
            while (lab > 0):
                pallete[j * 3 + 0] |= (((lab >> 0) & 1) << (7 - i))
                pallete[j * 3 + 1] |= (((lab >> 1) & 1) << (7 - i))
                pallete[j * 3 + 2] |= (((lab >> 2) & 1) << (7 - i))
                i = i + 1
                lab >>= 3
        return pallete

    def get_confusion_matrix(self, gt_label, pred_label, class_num):
        """
        Calcute the confusion matrix by given label and pred
        :param gt_label: the ground truth label
        :param pred_label: the pred label
        :param class_num: the nunber of class
        :return: the confusion matrix
        """
        index = (gt_label * class_num + pred_label).astype('int32')
        label_count = np.bincount(index)
        confusion_matrix = np.zeros((class_num, class_num))

        for i_label in range(class_num):
            for i_pred_label in range(class_num):
                cur_index = i_label * class_num + i_pred_label
                if cur_index < len(label_count):
                    confusion_matrix[i_label, i_pred_label] = label_count[cur_index]

        return confusion_matrix

    def _py_evaluate_segmentation(self):
        """
        This function is a wrapper to calculte the metrics for given pred_segmentation results
        :param pred_segmentations: the pred segmentation result
        :return: the evaluation metrics
        """
        confusion_matrix = np.zeros((self.num_classes, self.num_classes))
        result_dir = os.path.join(self.result_path, 'results', 'VOC' + self.year, 'Segmentation')

        for i, index in enumerate(self.image_set_index):
            seg_gt_info = self.load_pascal_segmentation_annotation(index)
            seg_gt_path = seg_gt_info['seg_cls_path']
            seg_gt = np.array(PIL.Image.open(seg_gt_path)).astype('float32')
            seg_pred_path = os.path.join(result_dir, '%s.png' % (index))
            seg_pred = np.array(PIL.Image.open(seg_pred_path)).astype('float32')

            seg_gt = cv2.resize(seg_gt, (seg_pred.shape[1], seg_pred.shape[0]), interpolation=cv2.INTER_NEAREST)
            ignore_index = seg_gt != 255
            seg_gt = seg_gt[ignore_index]
            seg_pred = seg_pred[ignore_index]

            confusion_matrix += self.get_confusion_matrix(seg_gt, seg_pred, self.num_classes)

        pos = confusion_matrix.sum(1)
        res = confusion_matrix.sum(0)
        tp = np.diag(confusion_matrix)

        IU_array = (tp / np.maximum(1.0, pos + res - tp))
        mean_IU = IU_array.mean()

        return {'meanIU': mean_IU, 'IU_array': IU_array}

    def get_result_file_template(self):
        """
        this is a template
        VOCdevkit/results/VOC2007/Main/<comp_id>_det_test_aeroplane.txt
        :return: a string template
        """
        res_file_folder = os.path.join(self.result_path, 'results', 'VOC' + self.year, 'Main')
        comp_id = self.config['comp_id']
        filename = comp_id + '_det_' + self.image_set + '_{:s}.txt'
        path = os.path.join(res_file_folder, filename)
        return path

    def write_pascal_results(self, all_boxes):
        """
        write results files in pascal devkit path
        :param all_boxes: boxes to be processed [bbox, confidence]
        :return: None
        """
        for cls_ind, cls in enumerate(self.classes):
            if cls == '__background__':
                continue
            print('Writing {} VOC results file'.format(cls))
            filename = self.get_result_file_template().format(cls)
            with open(filename, 'wt') as f:
                for im_ind, index in enumerate(self.image_set_index):
                    dets = all_boxes[cls_ind][im_ind]
                    if len(dets) == 0:
                        continue
                    # the VOCdevkit expects 1-based indices
                    for k in range(dets.shape[0]):
                        f.write('{:s} {:.3f} {:.1f} {:.1f} {:.1f} {:.1f}\n'.
                                format(index, dets[k, -1],
                                       dets[k, 0] + 1, dets[k, 1] + 1, dets[k, 2] + 1, dets[k, 3] + 1))

    def do_python_eval(self):
        """
        python evaluation wrapper
        :return: info_str
        """
        info_str = ''
        annopath = os.path.join(self.data_path, 'Annotations', '{0!s}.xml')
        imageset_file = os.path.join(self.data_path, 'ImageSets', 'Main', self.image_set + '.txt')
        annocache = os.path.join(self.cache_path, self.name + '_annotations.pkl')
        aps = []
        # The PASCAL VOC metric changed in 2010
        use_07_metric = True if self.year == 'SDS' or int(self.year) < 2010 else False
        print('VOC07 metric? ' + ('Y' if use_07_metric else 'No'))
        info_str += 'VOC07 metric? ' + ('Y' if use_07_metric else 'No')
        info_str += '\n'
        for cls_ind, cls in enumerate(self.classes):
            if cls == '__background__':
                continue
            filename = self.get_result_file_template().format(cls)
            rec, prec, ap = voc_eval(filename, annopath, imageset_file, cls, annocache,
                                     ovthresh=0.5, use_07_metric=use_07_metric)
            aps += [ap]
            print('AP for {} = {:.4f}'.format(cls, ap))
            info_str += 'AP for {} = {:.4f}\n'.format(cls, ap)
        print('Mean AP@0.5 = {:.4f}'.format(np.mean(aps)))
        info_str += 'Mean AP@0.5 = {:.4f}\n\n'.format(np.mean(aps))
        # @0.7
        aps = []
        for cls_ind, cls in enumerate(self.classes):
            if cls == '__background__':
                continue
            filename = self.get_result_file_template().format(cls)
            rec, prec, ap = voc_eval(filename, annopath, imageset_file, cls, annocache,
                                     ovthresh=0.7, use_07_metric=use_07_metric)
            aps += [ap]
            print('AP for {} = {:.4f}'.format(cls, ap))
            info_str += 'AP for {} = {:.4f}\n'.format(cls, ap)
        print('Mean AP@0.7 = {:.4f}'.format(np.mean(aps)))
        info_str += 'Mean AP@0.7 = {:.4f}'.format(np.mean(aps))
        return info_str
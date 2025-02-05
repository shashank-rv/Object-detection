import numpy as np

def preprocess_true_boxes(true_boxes, input_shape, anchors):
    
    #assert (true_boxes[..., 4]<num_classes).all(), 'class id must be less than num_classes'
    #num_layers = len(anchors)//3 # default setting
    num_layers = 3
    anchor_mask = [[6,7,8], [3,4,5], [0,1,2]] #if num_layers==3 else [[3,4,5], [1,2,3]]

    true_boxes = np.array(true_boxes, dtype='float32')
    input_shape = np.array(input_shape, dtype='int32')
    boxes_xy = ((true_boxes[..., 1:3] + true_boxes[...,3:5]) + (true_boxes[...,1:3]))//2
    boxes_wh = true_boxes[...,3:5]
    #true_boxes[..., 0:2] = boxes_xy/input_shape[::-1]
    #true_boxes[..., 2:4] = boxes_wh/input_shape[::-1]

    m = true_boxes.shape[0]
    #grid_shapes = [input_shape//{0:32, 1:16, 2:8}[l] for l in range(num_layers)]
    y_true = np.zeros((m,64,64,3,5),dtype='float32')

    # Expand dim to apply broadcasting.
    anchors = np.expand_dims(anchors, 0)
    anchor_maxes = anchors / 2.
    anchor_mins = -anchor_maxes
    valid_mask = boxes_wh[..., 0]>0

    for b in range(m):
        # Discard zero rows.
        wh = boxes_wh[b, valid_mask[b]]
        if len(wh)==0: continue
        # Expand dim to apply broadcasting.
        wh = np.expand_dims(wh, -2)
        box_maxes = wh / 2.
        box_mins = -box_maxes

        intersect_mins = np.maximum(box_mins, anchor_mins)
        intersect_maxes = np.minimum(box_maxes, anchor_maxes)
        intersect_wh = np.maximum(intersect_maxes - intersect_mins, 0.)
        intersect_area = intersect_wh[..., 0] * intersect_wh[..., 1]
        box_area = wh[..., 0] * wh[..., 1]
        anchor_area = anchors[..., 0] * anchors[..., 1]
        iou = intersect_area / (box_area + anchor_area - intersect_area)

        # Find best anchor for each true box
        best_anchor = np.argmax(iou, axis=-1)

        for t, n in enumerate(best_anchor):
            for l in range(num_layers):
                if n in anchor_mask[l]:
                    i = np.floor(true_boxes[b,t,1]/16).astype('int32')
                    j = np.floor(true_boxes[b,t,2]/16).astype('int32')
                    k = anchor_mask[l].index(n)
                    #c = true_boxes[b,t, 4].astype('int32')
                    y_true[b, j, i, k, 1:5] = true_boxes[b,t, 1:5]
                    y_true[b, j, i, k, 0] = 1
                    #y_true[l][b, j, i, k, 5+c] = 1

    return y_true
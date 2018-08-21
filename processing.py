def load_block(path, key="data"):
    """
    This function loads a h5 (neuro) block
    :param path: path to block
    :param key: key in the h5 file
    :return: block as np.array
    """

    import h5py
    import numpy as np
    file = h5py.File(path, 'r')

    return np.array(file[key])


def load_all_blocks(folder_path):
    """
    Returns array with all the blocks in one directory
    :param folder_path: path to folder with blocks
    :return: list with blocks
    """

    import os

    gt_files=os.listdir(folder_path)

    block_list=[]

    for file in gt_files:

        block_path=os.path.join(folder_path,file)

        block_list.append(load_block(block_path))

    return block_list


def extract_boundaries(img, connectivity=3):
    """
    Extracts binary mask with boundaries as ones
    :param img: labeled image
    :param connectivity: connectivity for neighbors in boundary detection
    :return: binary mask in int8 with boundaries
    """

    from skimage.segmentation import find_boundaries

    return find_boundaries(img, connectivity=connectivity).astype("int8")

def crop_blocks(big_blocks_array, window_size=80, stride=40, save_path = "../array_small_blocks.npy"):
    """
    Crops blocks for training
    :param big_blocks_array: list with blocks to crop
    :param window_size: size of qubic windows
    :param stride: stride of sliding window
    :return: array with all the cropped blocks
    """

    import numpy as np
    import os

    if os.path.exists(save_path):

        print("{} exists, loading...".format(save_path))
        array_small_blocks = np.load(save_path)
        print("loaded")

        return array_small_blocks

    else:

        array_small_blocks=[]

        for block_idx, big_block in enumerate(big_blocks_array):

            print("Cropping block {}".format(block_idx))

            dim1, dim2, dim3 = big_block.shape

            parts_dim1, parts_dim2, parts_dim3 = (dim1 - window_size)/stride+1, (dim2 - window_size)/stride+1, (dim3 - window_size)/stride+1

            assert(parts_dim1.is_integer()), "Dimension 1 does does not match window_size and stride"
            assert(parts_dim2.is_integer()), "Dimension 2 does does not match window_size and stride"
            assert(parts_dim3.is_integer()), "Dimension 3 does does not match window_size and stride"

            for count1 in np.arange(parts_dim1):
                for count2 in np.arange(parts_dim2):
                    for count3 in np.arange(parts_dim3):

                        array_small_blocks.append(big_block[int(count1) * stride : window_size + int(count1) * stride,
                                                   int(count2) * stride : window_size + int(count2) * stride,
                                                   int(count3) * stride : window_size + int(count3) * stride])


        print("saving to {}".format(save_path))
        np.save(save_path, array_small_blocks)
        print("saved")

        return np.array(array_small_blocks)


def load_crop_split_save_raw_gt(paths_dict):

    import numpy as np
    import os

    train_folder = os.path.join(paths_dict["project_folder"], "train/")
    val_folder = os.path.join(paths_dict["project_folder"], "val/")

    if os.path.exists(train_folder + "raw_train.npy") and \
            os.path.exists(train_folder + "gt_train.npy") and \
            os.path.exists(val_folder + "raw_val.npy") and \
            os.path.exists(val_folder + "gt_val.npy"):

        print("Cropped blocks already exist, loading...")
        cropped_array = [np.load(train_folder + "raw_train.npy"),
                         np.load(train_folder + "gt_train.npy"),
                         np.load(val_folder + "raw_val.npy"),
                         np.load(val_folder + "gt_val.npy")]
        print("loaded")
        return cropped_array


    else:

        raw_folder_path = os.path.join(paths_dict["blocks_folder_path"], paths_dict["raw_folder"])
        gt_folder_path = os.path.join(paths_dict["blocks_folder_path"], paths_dict["gt_folder"])

        print("loading all blocks")
        raw_blocks_all = load_all_blocks(raw_folder_path)
        gt_blocks_all_labeled = load_all_blocks(gt_folder_path)

        print("extracting boundaries from gt")
        gt_blocks_all = list(map(lambda x: extract_boundaries(x), gt_blocks_all_labeled))


        #if folders do not exist
        if not os.path.exists(train_folder):
            os.makedirs(train_folder)
        if not os.path.exists(val_folder):
            os.makedirs(val_folder)


        raw_train = raw_blocks_all[:int(len(raw_blocks_all)/2)]
        gt_train = gt_blocks_all[:int(len(gt_blocks_all)/2)]
        raw_val = raw_blocks_all[int(len(raw_blocks_all)/2):]
        gt_val = gt_blocks_all[int(len(gt_blocks_all)/2):]

        print("cropping all blocks...")
        cropped_array = [crop_blocks(raw_train, save_path = train_folder + "raw_train.npy"),
                         crop_blocks(gt_train, save_path = train_folder + "gt_train.npy"),
                         crop_blocks(raw_val, save_path = val_folder + "raw_val.npy"),
                         crop_blocks(gt_val, save_path = val_folder + "gt_val.npy")]

        return cropped_array



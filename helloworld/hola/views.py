from django.shortcuts import render
from django.views.generic import ListView
from PIL import Image
import os,pickle,argparse
from Trainer import DataTrainer,ImageSequencer
from Stepper import Stepper
from django.http import HttpResponse, HttpRequest
from django.template.loader import render_to_string
from django.template import Context, loader
from django.contrib.auth.models import User
from .models import Test
import strgen
from strgen import StringGenerator





def generate_image(im_width,im_height,norder,pickle1,set,random_string):
    #print('\\\\')



    trainer = DataTrainer()
    stepper = Stepper()
    img_sequencer = ImageSequencer()

    parser = argparse.ArgumentParser(description='Collect and curate a dataset of images.')
    parser.add_argument('directory', nargs=1)
    parser.add_argument('--size', nargs=2, type=int)
    parser.add_argument('--norder', nargs=1, type=int)
    parser.add_argument('--pickle', nargs=1, type=bool)

    #args = parser.parse_args()
    #print('///')
    #b= os.path.dirname('../templates/index.html')
    #print(os.path.dirname(b))

    directory = './' + str(set) + '/'
    im_width = im_width
    im_height = im_height
    norder = norder #args.norder[0]

    try:
        should_pickle = pickle1
    except:
        should_pickle = False

    pickle_file_name = "{width}-{height}-{norder}.pickle".format(width=im_width, height=im_height, norder=norder)
    pickled_data = {}
    preexisting_pickle = False

    if should_pickle:
        has_pickle = os.path.isfile(directory + pickle_file_name)
        if has_pickle:
            print('Loading Pickled Data...')
            with open(directory + pickle_file_name, 'rb') as pickle_file:
                    pickled_data = pickle.load(pickle_file)

    if pickled_data:
        trained_data = pickled_data
        preexisting_pickle = True
    else:
        image_set = []
        for fn in os.listdir(directory):
            if fn[0] != '.' and fn[-7:] !=".pickle":
                image_set.append(directory + fn)

        concat_text = ""

        for image in image_set:
            image = Image.open(image)
            image_as_text = img_sequencer.sequence_image_to_text(image)
            concat_text = concat_text + ' ' + image_as_text

        concat_text.strip()


        trained_data = trainer.train_text_data(
        raw_text = concat_text,
        order = norder,
        )

    # saves pickeled data
    if should_pickle and preexisting_pickle == False:
        print('Pickling data for later use...')
        with open(directory + pickle_file_name, 'wb+') as pickle_file:
            pickle.dump(trained_data, pickle_file)
            pickle_file.close()

    #print('Stepping Image Sequence...')

    gen_seq = stepper.new_set_length_sequence(
            model = trained_data,
            steps = im_width * im_height
            )

    #print('Generating Image...')
    image = img_sequencer.convert_text_to_image(gen_seq, im_width, im_height)


    print('saving')
    image.save("data/processed/images/" + str(set) + "-" + random_string + ".png")
    # print(gen_seq)


def homePageView(request,im_width,im_height,norder,pickle1,set):
    #im_width = request.GET.get('im_width')
    #im_height = request.GET.get('im_height')
    #norder = request.GET.get('norder')
    if pickle1 == 'True':
        pickle1 = True
    elif pickle1 == 'False':
        pickle1 = False

    random_string = StringGenerator("[\d\w]{10}").render()

    generate_image(im_width,im_height,norder,pickle1,set,random_string)
    response = HttpResponse(content_type = "image/png")
    print(random_string)
    img = Image.open("data/processed/images/" + str(set) + "-" + random_string + ".png")
    img.save(response,'png')
    return response

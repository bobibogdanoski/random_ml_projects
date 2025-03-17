import kagglehub
import pandas as pd
import numpy as np
import os
import tensorflow as tf
from sklearn.metrics import classification_report
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.applications import ResNet50

path = kagglehub.dataset_download("masoudnickparvar/brain-tumor-mri-dataset")
print("Path to dataset: " + path)

# Real Image width and height is 512, 512 but it takes too long to train #
IMAGE_W = 224
IMAGE_H = 224
train = tf.keras.preprocessing.image_dataset_from_directory(
    os.path.join(path, "Training"),
    label_mode = "int",
    batch_size = 32,
    image_size=(IMAGE_W, IMAGE_H),
)

test = tf.keras.preprocessing.image_dataset_from_directory(
    os.path.join(path, "Testing"),
    label_mode = "int",
    batch_size = 32,
    image_size=(IMAGE_W, IMAGE_H),
)

#train_ds = train.map(lambda x, y: (x / 255.0, y))

amount_labels = len(train.class_names)

train = train.shuffle(buffer_size=1000).cache().prefetch(tf.data.AUTOTUNE)
test = test.shuffle(buffer_size=1000).cache().prefetch(tf.data.AUTOTUNE)

data_aug = tf.keras.Sequential([
    tf.keras.layers.RandomFlip(),
    tf.keras.layers.RandomRotation(0.3),
    tf.keras.layers.RandomTranslation(0.2, 0.2),
])

model = None

if os.path.exists("brain_tumor_cnn.keras"):
    model = tf.keras.models.load_model('brain_tumor_cnn.keras')
else:
    base_model = ResNet50(
        weights="imagenet",
        include_top=False,
        input_shape=(IMAGE_W, IMAGE_H, 3)
    )

    base_model.trainable = False

    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(IMAGE_W, IMAGE_H, 3)),
        data_aug,
        tf.keras.layers.Rescaling(1./255),
        base_model,
        #tf.keras.layers.Conv2D(32, (3,3), activation="relu"),
        #tf.keras.layers.MaxPooling2D((2,2)),
        #tf.keras.layers.Dropout(0.1),
        #tf.keras.layers.Conv2D(64, (3,3), activation="relu"),
        #tf.keras.layers.MaxPooling2D((2,2)),
        #tf.keras.layers.Dropout(0.1),
        #tf.keras.layers.Flatten(),
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(512, activation="relu"),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(amount_labels, activation="softmax"),
    ])

    model.compile(
        loss = "sparse_categorical_crossentropy",
        optimizer = "Adam",
        metrics = ["accuracy"]
    )

    early_stopping = EarlyStopping(monitor='val_loss', patience=3)

    model.fit(train, epochs=10, validation_data=test, callbacks=[early_stopping])
    model.save('brain_tumor_cnn.keras')

y_test = np.empty((0), dtype=int)
for x, y in test:
    y_test = np.concatenate((y_test, y.numpy()))

y_pred = model.predict(test)
y_pred = np.argmax(y_pred, axis=-1)

print(classification_report(y_test, y_pred))
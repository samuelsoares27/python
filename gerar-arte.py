import tensorflow as tf
from tensorflow.keras import layers
import numpy as np
import matplotlib.pyplot as plt
import logging

# Configuração do logging
logging.basicConfig(level=logging.DEBUG,  # Define o nível de log (DEBUG mostra tudo)
                    format='%(asctime)s - %(levelname)s - %(message)s',  # Formato das mensagens
                    handlers=[logging.FileHandler("training.log"),  # Registra no arquivo
                              logging.StreamHandler()])  # Também imprime no console

# Função para criar a rede geradora
def build_generator():
    model = tf.keras.Sequential()
    model.add(layers.Dense(7 * 7 * 256, use_bias=False, input_shape=(100,)))
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())
    model.add(layers.Reshape((7, 7, 256)))
    model.add(layers.Conv2DTranspose(128, (5, 5), strides=(1, 1), padding='same', use_bias=False))
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())
    model.add(layers.Conv2DTranspose(64, (5, 5), strides=(2, 2), padding='same', use_bias=False))
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())
    model.add(layers.Conv2DTranspose(1, (5, 5), strides=(2, 2), padding='same', use_bias=False, activation='tanh'))
    return model

# Função para criar a rede discriminadora
def build_discriminator():
    model = tf.keras.Sequential()
    model.add(layers.Conv2D(64, (5, 5), strides=(2, 2), padding='same', input_shape=[28, 28, 1]))
    model.add(layers.LeakyReLU())
    model.add(layers.Dropout(0.3))
    model.add(layers.Conv2D(128, (5, 5), strides=(2, 2), padding='same'))
    model.add(layers.LeakyReLU())
    model.add(layers.Dropout(0.3))
    model.add(layers.Flatten())
    model.add(layers.Dense(1))
    return model

# Função de perda e otimização
cross_entropy = tf.keras.losses.BinaryCrossentropy(from_logits=True)

def generator_loss(fake_output):
    return cross_entropy(tf.ones_like(fake_output), fake_output)

def discriminator_loss(real_output, fake_output):
    real_loss = cross_entropy(tf.ones_like(real_output), real_output)
    fake_loss = cross_entropy(tf.zeros_like(fake_output), fake_output)
    return real_loss + fake_loss

# Função para gerar e salvar imagens
def generate_and_plot_images(model, test_input, epoch):
    logging.info(f"Iniciando a geração de imagens para a época {epoch}...")
    try:
        predictions = model(test_input, training=False)
        plt.figure(figsize=(4, 4))
        for i in range(predictions.shape[0]):
            plt.subplot(4, 4, i + 1)
            plt.imshow(predictions[i, :, :, 0] * 127.5 + 127.5, cmap='gray')
            plt.axis('off')
        plt.savefig(f"image_at_epoch_{epoch}.png")
        plt.show()
        logging.info(f"Imagens geradas e salvas para a época {epoch}.")
    except Exception as e:
        logging.error(f"Erro ao gerar e salvar imagens: {e}")

# Preparando os dados (MNIST)
logging.info("Carregando dados MNIST...")
(train_images, _), (_, _) = tf.keras.datasets.mnist.load_data()
train_images = train_images.reshape(train_images.shape[0], 28, 28, 1).astype('float32')
train_images = (train_images - 127.5) / 127.5  # Normalizar para [-1, 1]
logging.info("Dados MNIST carregados e normalizados.")

BUFFER_SIZE = 60000
BATCH_SIZE = 256
train_dataset = tf.data.Dataset.from_tensor_slices(train_images).shuffle(BUFFER_SIZE).batch(BATCH_SIZE)

# Construção do modelo
logging.info("Construindo os modelos gerador e discriminador...")
generator = build_generator()
discriminator = build_discriminator()

# Otimizadores
generator_optimizer = tf.keras.optimizers.Adam(1e-4)
discriminator_optimizer = tf.keras.optimizers.Adam(1e-4)

# Função para treinar o modelo
epochs = 50
noise_dim = 100
seed = tf.random.normal([16, noise_dim])

for epoch in range(epochs):
    logging.info(f"Iniciando a época {epoch + 1}...")
    try:
        for image_batch in train_dataset:
            noise = tf.random.normal([BATCH_SIZE, noise_dim])

            with tf.GradientTape() as gen_tape, tf.GradientTape() as disc_tape:
                generated_images = generator(noise, training=True)
                real_output = discriminator(image_batch, training=True)
                fake_output = discriminator(generated_images, training=True)

                gen_loss = generator_loss(fake_output)
                disc_loss = discriminator_loss(real_output, fake_output)

            gradients_of_generator = gen_tape.gradient(gen_loss, generator.trainable_variables)
            gradients_of_discriminator = disc_tape.gradient(disc_loss, discriminator.trainable_variables)

            generator_optimizer.apply_gradients(zip(gradients_of_generator, generator.trainable_variables))
            discriminator_optimizer.apply_gradients(zip(gradients_of_discriminator, discriminator.trainable_variables))

        logging.info(f"Época {epoch + 1} concluída. Gen Loss: {gen_loss.numpy()}, Disc Loss: {disc_loss.numpy()}")
        generate_and_plot_images(generator, seed, epoch + 1)
    except Exception as e:
        logging.error(f"Erro durante a época {epoch + 1}: {e}")

logging.info("Treinamento concluído.")

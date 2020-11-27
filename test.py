from nyumaya_hotword_plugin.libnyumaya import AudioRecognition, FeatureExtractor
import time
from datetime import datetime
from nyumaya_hotword_plugin.record import ArecordStream


def label_stream(labels, graph, sensitivity):
    audio_stream = ArecordStream()

    extractor = FeatureExtractor()
    extactor_gain = 1.0

    detector = AudioRecognition(graph, labels)
    detector.set_sensitivity(sensitivity)

    bufsize = detector.get_input_data_size()

    print("Version: " + detector.version)

    audio_stream.start()
    try:
        while True:
            frame = audio_stream.read(bufsize * 2, bufsize * 2)
            if not frame:
                time.sleep(0.01)
                continue

            features = extractor.signal_to_mel(frame, extactor_gain)

            prediction = detector.run_detection(features)

            if prediction:
                now = datetime.now().strftime("%d.%b %Y %H:%M:%S")
                print(detector.get_prediction_label(prediction) + " " + now)

    except KeyboardInterrupt:
        print("Terminating")
        audio_stream.stop()


if __name__ == '__main__':
    import argparse
    from os.path import dirname, join
    default_model = join(dirname(__file__), "nyumaya_hotword_plugin",
                         "models", "hotwords", "alexa_small_0.3.tflite")
    default_labels = join(dirname(__file__), "nyumaya_hotword_plugin",
                         "models", "hotwords", "alexa_labels.txt")

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--model', type=str,
        default=default_model,
        help='Model to use for identification.')

    parser.add_argument(
        '--labels', type=str,
        default=default_labels,
        help='Path to file containing labels.')

    parser.add_argument(
        '--sens', type=float,
        default='0.5',
        help='Sensitivity for detection. A lower value means more sensitivity, for example,'
             '0.1 will lead to less false positives, but will also be harder to trigger.'
             '0.9 will make it easier to trigger, but lead to more false positives')

    FLAGS, unparsed = parser.parse_known_args()

    label_stream(FLAGS.labels, FLAGS.model, FLAGS.sens)

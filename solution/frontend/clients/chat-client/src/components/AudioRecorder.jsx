import React, { useState, useRef } from 'react';
import { Mic, SendHorizonal , Loader2 } from 'lucide-react';

const AudioRecorder = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);

  const audioRef = useRef(null);

  // Get the most efficient supported MIME type
  const getOptimalMimeType = () => {
    const types = [
      'audio/webm;codecs=opus',  // Opus in WebM container (very efficient)
      'audio/ogg;codecs=opus',   // Opus in Ogg container
      'audio/webm',              // Fallback to default WebM
      'audio/ogg'                // Fallback to Ogg
    ];

    return types.find(type => MediaRecorder.isTypeSupported(type)) || 'audio/webm';
  };

  const startRecording = async () => {
    try {
      if (audioRef.current) {
        audioRef.current.pause();
      }
      window.setEmotion('neutral');

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,         // Mono audio
          sampleRate: 16000,       // Lower sample rate
          echoCancellation: true,  // Reduce echo
          noiseSuppression: true   // Reduce background noise
        }
      });

      const mimeType = getOptimalMimeType();
      console.log('Using MIME type:', mimeType);

      mediaRecorder.current = new MediaRecorder(stream, {
        mimeType,
        audioBitsPerSecond: 32000  // Lower bitrate for smaller file size
      });

      mediaRecorder.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.current.push(event.data);
        }
      };

      mediaRecorder.current.onstop = async () => {
        const audioBlob = new Blob(audioChunks.current, { type: mimeType });
        console.log('Audio size:', Math.round(audioBlob.size / 1024), 'KB');
        await sendAudioToServer(audioBlob);
      };

      // Request data every second instead of waiting until stop
      // This allows for streaming-like behavior and earlier transmission start
      audioChunks.current = [];
      mediaRecorder.current.start(1000);
      setIsRecording(true);
      setError('');
    } catch (err) {
      setError('Error accessing microphone: ' + err.message);
      console.error('Recording error:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  const sendAudioToServer = async (audioBlob) => {
    setIsProcessing(true);
    try {
      const formData = new FormData();
      // Add the MIME type to the filename so server knows the format
      const mimeType = mediaRecorder.current.mimeType;
      const extension = mimeType.includes('ogg') ? 'ogg' : 'webm';
      formData.append('audio', audioBlob, `recording.${extension}`);

      const resolved_options = Intl.DateTimeFormat().resolvedOptions();
      const response = await fetch('https://service-1.ngrok.io/api/upload-audio', {
        method: 'POST',
        headers: {
          'X-Timezone': resolved_options.timeZone,
          'X-Locale': resolved_options.locale
        },
        body: formData,
      });

      const emotion = response.headers.get('X-Emotion');
      window.setEmotion(emotion);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Get the blob from the response
      const blob = await response.blob();

      // Create a URL for the blob
      const audioUrl = URL.createObjectURL(blob);

      // Set the audio source and play
      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        audioRef.current.playbackRate = 1.1;

        // Wait for the audio to load before playing
        audioRef.current.onloadeddata = () => {
          audioRef.current.play()
            .catch(e => {
              setError('Failed to play audio automatically.');
              console.error('Autoplay failed:', e);
            });
        };

        audioRef.current.onended = () => {
          window.setEmotion('neutral');
        };
      }
    } catch (err) {
      setError('Error sending audio: ' + err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-x-0 bottom-0 flex justify-center pb-0 xl:pb-4 2xl:pb-8" style={{ zIndex: 1 }}>
      <div className="flex flex-col items-center gap-3 p-0 xl:p-4 2xl:p-8 max-w-md">
        <div className="flex items-center justify-center 2xl:w-28 2xl:h-28 lg:w-24 lg:h-24 sm:w-20 sm:h-20 rounded-full bg-gray-100">
          {isProcessing ? (
            <Loader2 className="2xl:w-10 2xl:h-10 lg:w-12 lg:h-12 sm:w-8 sm:h-8 text-pink-500 animate-spin spin-fast" />
          ) : isRecording ? (
            <button
              onClick={stopRecording}
              className="flex items-center justify-center lg:w-20 lg:h-20 sm:w-16 sm:h-16 rounded-full bg-green-500 hover:bg-green-600 active:bg-green-700 transition-colors touch-manipulation"
              aria-label="Stop recording"
            >
              <SendHorizonal className="2xl:w-10 2xl:h-10 lg:w-12 lg:h-12 sm:w-8 sm:h-8 text-white" />
            </button>
          ) : (
            <button
              onClick={startRecording}
              className="flex items-center justify-center lg:w-20 lg:h-20 sm:w-16 sm:h-16 rounded-full bg-pink-500 hover:bg-pink-600 active:bg-pink-700 transition-colors touch-manipulation"
              aria-label="Start recording"
            >
              <Mic className="2xl:w-10 2xl:h-10 lg:w-12 lg:h-12 sm:w-8 sm:h-8 text-white" />
            </button>
          )}

          <audio
            ref={audioRef}
            onError={(e) => setError('Error loading audio file')}
            className="sr-only"
          />
        </div>

        <div className="text-center">
          {/* {isRecording && (
            <p className="text-red-500 font-medium">Recording in progress...</p>
          )}
          {isProcessing && (
            <p className="text-blue-500 font-medium">Processing audio...</p>
          )} */}
          {error && (
            <p className="text-red-500 mt-2 text-sm sm:text-base">{error}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default AudioRecorder;
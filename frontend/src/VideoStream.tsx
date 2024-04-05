import React, { useState, useEffect, useRef } from "react";

const VideoStream = () => {
  const videoRef = useRef<any>(null);
  const [isStreamVisible, setIsStreamVisible] = useState(true);

  useEffect(() => {
    // Assuming the stream should be visible initially
    if (videoRef.current) {
      videoRef.current.src = isStreamVisible
        ? "http://localhost:5000/video"
        : "";
    }
  }, [isStreamVisible]);

  const toggleStreamVisibility = () => {
    setIsStreamVisible(!isStreamVisible);
  };

  return (
    <div className="relative h-full w-full">
      {isStreamVisible && (
        <img
          className="w-full h-full object-cover"
          ref={videoRef}
          alt="Video Stream"
        />
      )}
      <button
        onClick={toggleStreamVisibility}
        className="absolute top-3 right-3 bg-purple-500 text-white p-2 rounded-full z-10"
      >
        {isStreamVisible ? "Turn Off" : "Turn On"}
      </button>
    </div>
  );
};

export default VideoStream;

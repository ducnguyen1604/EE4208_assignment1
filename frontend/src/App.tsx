import React, { useState } from "react";
import logo from "./logo.svg";
import "./App.css";
import { AiOutlineHome } from "react-icons/ai";
import VideoStream from "./VideoStream";
import axios from "axios";

function App() {
  const [latestFaceUrl, setLatestFaceUrl] = useState("");

  const updateFaceInformation = async () => {
    try {
      const response = await axios({
        method: "get",
        url: "http://localhost:5000/latest_face",
        responseType: "blob", // Important to handle images
      });

      // Create a URL for the blob
      const url = window.URL.createObjectURL(new Blob([response.data]));
      setLatestFaceUrl(url);
    } catch (error) {
      console.error("Failed to fetch latest face", error);
      // Handle error or set a default image
    }
  };
  return (
    <div className="bg-purple-500 p-5 min-h-screen flex flex-col justify-center">
      <div className="text-white text-lg font-bold text-center mb-5">
        COURSE ASSIGNMENT
      </div>
      <div className="flex flex-1 min-h-0">
        <div className="flex-1 mr-5 border-4 rounded-md overflow-hidden">
          <div className="bg-black h-full text-white">
            <VideoStream />
          </div>
        </div>
        <div className=" w-1/3 flex flex-col">
          <div className="bg-white p-3 rounded-md mb-2 flex-grow">
            <div className="flex flex-col justify-between items-center h-full bg-white p-3">
              <div className="bg-black border-4 border-purple-500 h-40 w-40 mb-3 rounded-md">
                {latestFaceUrl && (
                  <img
                    src={latestFaceUrl}
                    alt="Latest Detected Face"
                    className="w-full h-full object-cover"
                  />
                )}
              </div>
              <div className="text-center mb-3">
                <div className="flex justify-center">
                  <p className="">Classified: </p>
                  <p className="font-bold"> Human</p>
                </div>
              </div>
              <button
                onClick={updateFaceInformation}
                className="bg-purple-500 text-white p-2 w-full rounded-md"
              >
                Detect Information
              </button>
            </div>
          </div>

          <div className="bg-white p-3 mt-2 rounded-md">
            <div className="relative p-4 flex flex-col h-64">
              <div className="flex-grow flex flex-col items-center justify-startpx-2">
                <button className="bg-purple-500 text-white p-2 mt-1 mb-2 w-full rounded-md">
                  Face Detection
                </button>
                <button className="bg-purple-200 text-white p-2 mb-2 w-full rounded-md">
                  Edge Detection
                </button>
              </div>

              <div className="flex justify-between mt-2">
                <button className="flex-1 flex justify-center items-center bg-purple-500 text-white p-2 text-lg font-bold ">
                  <AiOutlineHome /> Home
                </button>
                <button className="flex-1 flex justify-center items-center bg-purple-200 text-white p-2 text-lg font-bold">
                  <AiOutlineHome /> Exit
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;

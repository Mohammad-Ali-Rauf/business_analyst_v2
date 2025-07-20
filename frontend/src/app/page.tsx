'use client'

import { useState, useEffect } from "react";
import axios from "axios";
import Markdown from "react-markdown";

export default function Home() {
  const [feature, setFeature] = useState("");
  const [story, setStory] = useState("");
  const [token, setToken] = useState("");
  const [loading, setLoading] = useState(false);
  const [audioFile, setAudioFile] = useState(null);
  const [transcript, setTranscript] = useState("");

  useEffect(() => {
    let userToken = localStorage.getItem("user_token");
    if (!userToken) {
      userToken = crypto.randomUUID();
      localStorage.setItem("user_token", userToken);
    }
    setToken(userToken);
  }, []);

  async function generateUserStory() {
    if (!feature.trim()) return alert("Type something first, bruh!");
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("text", feature);
      formData.append("token", token);

      const res = await axios.post("http://localhost:8000/generate_from_text", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const data = res.data;
      console.log(data)
      setStory(data.story);
    } catch (e) {
      setStory("Error: " + e.message);
    }
    setLoading(false);
  }

  async function uploadAudio() {
    if (!audioFile) return alert("Choose an audio file first!");
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", audioFile);
      formData.append("token", token);

      const res = await axios.post("http://localhost:8000/generate_from_audio", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const transcriptText = res.data.transcription || "";
      setTranscript(transcriptText);
      setFeature(transcriptText);
      setStory(res.data.story);

    } catch (e) {
      alert("Transcription failed: " + e.message);
    }
    setLoading(false);
  }

  return (
    <div className="min-h-screen bg-[#121212] text-gray-300 font-sans p-6 mx-auto">
      <h1 className="text-4xl font-bold text-red-600 mb-8 text-center select-none">
        Agile User Story Generator
      </h1>

      <div className="flex flex-col md:flex-row gap-8">
        {/* LEFT COLUMN - OUTPUT */}
        <div className="flex-1 bg-[#1e1e1e] rounded-md p-6 border border-red-700 min-h-[400px] flex flex-col">
          <h2 className="text-2xl font-semibold mb-4 text-red-600 select-none">Output</h2>

          <div className="flex-1 overflow-y-auto mb-6 max-h-[60vh] prose prose-invert text-gray-300">
            {story ? (
              <Markdown>
                {story}
              </Markdown>
            ) : (
              <p className="text-gray-500 italic">No story generated yet</p>
            )}
          </div>

        </div>

        {/* RIGHT COLUMN - INPUT */}
        <div className="flex-1 bg-[#1e1e1e] rounded-md p-6 border border-red-700 min-h-[400px] flex flex-col">
          <h2 className="text-2xl font-semibold mb-4 text-red-600 select-none">Input</h2>

          <textarea
            rows={6}
            placeholder="Type your feature or requirement here..."
            value={feature}
            onChange={(e) => setFeature(e.target.value)}
            className="w-full p-4 mb-5 rounded-md bg-[#121212] border border-red-600 text-gray-200 placeholder-red-500 focus:outline-none focus:ring-2 focus:ring-red-600 transition flex-grow resize-none"
          />

          <button
            onClick={generateUserStory}
            disabled={loading}
            className="w-full bg-red-600 hover:bg-red-700 text-black font-semibold py-3 rounded-md mb-6 transition disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? "Generating..." : "Generate User Story"}
          </button>

          <input
            type="file"
            accept="audio/*"
            onChange={(e) => setAudioFile(e.target.files[0])}
            className="mb-4 text-red-500"
          />

          <button
            onClick={uploadAudio}
            disabled={loading || !audioFile}
            className="w-full bg-red-600 hover:bg-red-700 text-black font-semibold py-3 rounded-md transition disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? "Transcribing..." : "Upload, Transcribe and Generate User Story"}
          </button>
        </div>
      </div>
    </div>
  );
}

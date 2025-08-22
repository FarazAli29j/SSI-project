let mediaRecorder;
let audioChunks = [];

export async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    audioChunks = [];

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data);
      }
    };

    mediaRecorder.start();
    console.log("🎤 Recording started...");
  } catch (err) {
    console.error("Mic error:", err);
    throw err;
  }
}

export async function stopRecording() {
  return new Promise((resolve, reject) => {
    if (!mediaRecorder) {
      return reject(new Error("No recording started"));
    }

    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
      console.log("🛑 Recording stopped. Blob ready:", audioBlob);
      resolve(audioBlob);
    };

    mediaRecorder.stop();
  });
}

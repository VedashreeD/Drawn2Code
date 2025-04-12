import React, { useRef, useState, useEffect } from 'react';
import './App.css';

function App() {
  const canvasRef = useRef(null);
  const [generatedHtml, setGeneratedHtml] = useState('');
  const [drawing, setDrawing] = useState(false);
  const [previewSrc, setPreviewSrc] = useState('');

  // Set white background when canvas mounts
  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = 'black';
    ctx.lineWidth = 2;
  }, []);

  const handleMouseDown = (e) => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.beginPath();
    ctx.moveTo(e.nativeEvent.offsetX, e.nativeEvent.offsetY);
    setDrawing(true);
  };

  const handleMouseMove = (e) => {
    if (!drawing) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.lineTo(e.nativeEvent.offsetX, e.nativeEvent.offsetY);
    ctx.stroke();
  };

  const handleMouseUp = () => {
    setDrawing(false);
  };

  const handleClear = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = 'black';
    ctx.lineWidth = 2;

    setGeneratedHtml('');
    setPreviewSrc(''); // Clear preview image when clearing canvas
  };

  const handleSend = () => {
    const canvas = canvasRef.current;

    canvas.toBlob(async (blob) => {
      if (!blob) {
        console.error('Failed to convert canvas to blob');
        return;
      }

      const formData = new FormData();
      formData.append('image', blob, 'drawing.jpg');

      try {
        const res = await fetch('http://localhost:8000/generate-html', {
          method: 'POST',
          body: formData,
        });

        const data = await res.json();
        console.log('HTML:', data.html);
        setGeneratedHtml(data.html);  // Set HTML code to display
      } catch (err) {
        console.error('Error:', err);
      }
    }, 'image/jpeg');
  };

  const handlePreview = () => {
    const canvas = canvasRef.current;
    const dataUrl = canvas.toDataURL('image/png'); // Use PNG to ensure better quality
    console.log('Previewing canvas:', dataUrl.slice(0, 100)); // Logs the first 100 characters of the base64 string

    if (!dataUrl) {
      console.error('Canvas toDataURL failed');
    }

    setPreviewSrc(dataUrl); // Set preview image source
  };

  return (
    <div style={{ textAlign: 'center' }}>
      <h1>Draw Your Webpage</h1>

      <canvas
        ref={canvasRef}
        width={500}
        height={500}
        style={{ border: '1px solid black' }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      ></canvas>
      <br />

      <button onClick={handleSend}>Generate HTML</button>
      <button onClick={handleClear}>Clear</button>
      <button onClick={handlePreview}>Preview Image</button>

      {/* Show the generated HTML code */}
      {generatedHtml && (
        <div>
          <h2>Generated Webpage</h2>
          <div
            style={{
              border: '1px solid #ccc',
              margin: '20px auto',
              padding: '10px',
              maxWidth: '600px',
              textAlign: 'left',
            }}
            dangerouslySetInnerHTML={{ __html: generatedHtml }}
          />
        </div>
      )}

      {/* Show canvas preview */}
      {previewSrc && (
        <div>
          <h3>Canvas Preview</h3>
          <img
            src={previewSrc}
            alt="Canvas Preview"
            style={{ marginTop: '10px', border: '1px solid gray' }}
          />
        </div>
      )}
    </div>
  );
}

export default App;

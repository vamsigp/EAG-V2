// Icon creation script - creates simple placeholder icons
// This would normally be replaced with proper icon files

const createIcon = (size, filename) => {
    const canvas = document.createElement('canvas');
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d');

    // Gradient background
    const gradient = ctx.createLinearGradient(0, 0, size, size);
    gradient.addColorStop(0, '#667eea');
    gradient.addColorStop(1, '#764ba2');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, size, size);

    // Icon symbol (magnifying glass)
    ctx.strokeStyle = 'white';
    ctx.fillStyle = 'white';
    ctx.lineWidth = size * 0.06;

    const centerX = size * 0.4;
    const centerY = size * 0.4;
    const radius = size * 0.15;

    // Circle
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.stroke();

    // Handle
    ctx.beginPath();
    ctx.moveTo(centerX + radius * 0.7, centerY + radius * 0.7);
    ctx.lineTo(centerX + radius * 1.4, centerY + radius * 1.4);
    ctx.stroke();

    // Download the icon
    canvas.toBlob(blob => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }, 'image/png');
};

// Note: This script would need to be run in a browser environment
// For now, you can create simple colored square icons manually or use any icon creation tool

console.log('Icon creation script ready. Run createIcon(16, "icon16.png") etc. in browser console.');
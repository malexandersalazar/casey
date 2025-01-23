function getRandomInterval(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

// LEDAnimator

const style = document.createElement('style');
style.textContent = `
    body, html {
        margin: 0;
        padding: 0;
        overflow: hidden;
        width: 100%;
        height: 100%;
        background-color: black;
    }
    #eve-container {
        width: 100%;
        height: 100%;
    }
`;
document.head.appendChild(style);

class EVELEDAnimator {
    constructor(containerId) {
        this.app = new PIXI.Application({
            width: window.innerWidth,
            height: window.innerHeight,
            backgroundColor: 0xFFFFFF,
            resolution: window.devicePixelRatio || 1,
            autoDensity: true,
            resizeTo: window
        });
        document.getElementById(containerId).appendChild(this.app.view);

        this.baseWidth = 2560;
        this.baseHeight = 1440;
        this.scaleFactor = Math.max(window.innerWidth / this.baseWidth, window.innerHeight / this.baseHeight);
        this.eyeDistance = 0.42;

        window.addEventListener('resize', this.resize.bind(this));

        if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
            this.scaleFactor = Math.max(window.innerHeight / this.baseWidth, window.innerWidth / this.baseHeight);
            screen.orientation.lock('landscape');
        }

        this.eyesContainer = new PIXI.Container();
        this.app.stage.addChild(this.eyesContainer);

        this.eyeContainers = [new PIXI.Container(), new PIXI.Container()];
        this.eyeContainers.forEach(container => this.eyesContainer.addChild(container));

        this.currentEmotion = 'neutral';
        this.targetEmotion = 'neutral';
        this.transitionProgress = 1;
        this.lookAtCoords = { x: 0.5, y: 0.5 };

        this.emotions = {
            neutral: [
                { width: Math.floor(100 * this.scaleFactor), height: Math.floor(60 * this.scaleFactor), curve: 0, intensity: 0.85, angle: 8, curveCut: 0, cutFromTop: false, edge: 0.16, cutInY: 0.0 },
                { width: Math.floor(100 * this.scaleFactor), height: Math.floor(60 * this.scaleFactor), curve: 0, intensity: 0.85, angle: -8, curveCut: 0, cutFromTop: false, edge: 0.16, cutInY: 0.0 }
            ],
            happy: [
                { width: Math.floor(80 * this.scaleFactor), height: Math.floor(80 * this.scaleFactor), curve: 0, intensity: 1.0, angle: 0, curveCut: 0.7, cutFromTop: false, edge: 0.08, cutInY: 0.0 },
                { width: Math.floor(80 * this.scaleFactor), height: Math.floor(80 * this.scaleFactor), curve: 0, intensity: 1.0, angle: 0, curveCut: 0.7, cutFromTop: false, edge: 0.08, cutInY: 0.0 }
            ],
            sad: [
                { width: Math.floor(90 * this.scaleFactor), height: Math.floor(80 * this.scaleFactor), curve: -0.2, intensity: 0.7, angle: -8, curveCut: 0.5, cutFromTop: false, edge: 0.32, cutInY: 0.20 },
                { width: Math.floor(90 * this.scaleFactor), height: Math.floor(80 * this.scaleFactor), curve: -0.2, intensity: 0.7, angle: 8, curveCut: 0.5, cutFromTop: false, edge: 0.32, cutInY: 0.20 }
            ],
            angry: [
                { width: Math.floor(90 * this.scaleFactor), height: Math.floor(45 * this.scaleFactor), curve: -0.3, intensity: 1.0, angle: 16, curveCut: 0.5, cutFromTop: true, edge: 0.24, cutInY: 0.0 },
                { width: Math.floor(90 * this.scaleFactor), height: Math.floor(45 * this.scaleFactor), curve: -0.3, intensity: 1.0, angle: -16, curveCut: 0.5, cutFromTop: true, edge: 0.24, cutInY: 0.0 }
            ],
            surprised: [
                { width: Math.floor(80 * this.scaleFactor), height: Math.floor(80 * this.scaleFactor), curve: 0, intensity: 1.0, angle: 0, curveCut: 0, cutFromTop: false, edge: 0.08, cutInY: 0.0 },
                { width: Math.floor(80 * this.scaleFactor), height: Math.floor(80 * this.scaleFactor), curve: 0, intensity: 1.0, angle: 0, curveCut: 0, cutFromTop: false, edge: 0.08, cutInY: 0.0 }
            ],
            fearful: [
                { width: Math.floor(60 * this.scaleFactor), height: Math.floor(60 * this.scaleFactor), curve: 0, intensity: 0.7, angle: -16, curveCut: 0.3, cutFromTop: true, edge: 0.32, cutInY: 0.0 },
                { width: Math.floor(60 * this.scaleFactor), height: Math.floor(60 * this.scaleFactor), curve: 0, intensity: 0.7, angle: 16, curveCut: 0.3, cutFromTop: true, edge: 0.32, cutInY: 0.0 }
            ],
            disgusted: [
                { width: Math.floor(100 * this.scaleFactor), height: Math.floor(80 * this.scaleFactor), curve: 0, intensity: 0.7, angle: -24, curveCut: 0.5, cutFromTop: true, edge: 0.24, cutInY: 0.0 },
                { width: Math.floor(100 * this.scaleFactor), height: Math.floor(80 * this.scaleFactor), curve: 0, intensity: 0.7, angle: -8, curveCut: 0.5, cutFromTop: true, edge: 0.24, cutInY: 0.0 }
            ]
        };

        this.currentEyeData = JSON.parse(JSON.stringify(this.emotions.neutral));
        this.targetEyeData = JSON.parse(JSON.stringify(this.emotions.neutral));

        this.ledSize = 8 * this.scaleFactor;
        this.ledSpacing = 1 * this.scaleFactor;
        this.maxWidth = Math.max(...Object.values(this.emotions).flatMap(e => e.map(eye => eye.width)));
        this.maxHeight = Math.max(...Object.values(this.emotions).flatMap(e => e.map(eye => eye.height)));
        this.createLEDEyes();

        this.blinkProgress = 0;
        this.blinkInterval = getRandomInterval(4000, 10000);
        this.lastBlinkTime = Date.now();
        this.blinkAgain = false;

        this.app.ticker.add(() => this.animate());
        this.resize();

        this.centerColor = 0xFE007A;//0x53AFF1;
        this.edgeColor = 0xFFFFFF;
    }

    resize() {
        this.app.renderer.resize(window.innerWidth, window.innerHeight);
        this.updateEyePositions();
    }

    createLEDEyes() {
        this.eyeContainers.forEach((container, index) => {
            const totalWidth = (this.ledSize + this.ledSpacing) * this.maxWidth;
            const totalHeight = (this.ledSize + this.ledSpacing) * this.maxHeight;

            for (let y = 0; y < this.maxHeight; y++) {
                for (let x = 0; x < this.maxWidth; x++) {
                    const led = new PIXI.Graphics();
                    led.beginFill(0xFE007A);
                    led.drawRect(0, 0, this.ledSize, this.ledSize);
                    led.endFill();
                    led.x = x * (this.ledSize + this.ledSpacing);
                    led.y = y * (this.ledSize + this.ledSpacing);
                    container.addChild(led);
                }
            }

            container.pivot.x = totalWidth / 2;
            container.pivot.y = totalHeight / 2;
        });

        const eyeDistance = Math.max(this.app.screen.width, this.app.screen.height) * 0.42;
        this.eyeContainers[0].x = -eyeDistance / 2;
        this.eyeContainers[1].x = eyeDistance / 2;
    }

    updateEyePositions() {
        const x = this.lookAtCoords.x * this.app.screen.width;
        const y = this.lookAtCoords.y * this.app.screen.height;
        this.eyesContainer.position.set(x, y);
    }

    setEmotions(emotionMap, dominantEmotion) {
        const normalizedEmotions = {};

        const total = Object.values(emotionMap).reduce((sum, value) => sum + value, 0);
        for (const [emotion, value] of Object.entries(emotionMap)) {
            normalizedEmotions[emotion] = value / total;
        }
        this.targetEyeData = this.currentEyeData.map((_, eyeIndex) => {
            const blendedEyeData = {
                width: 0, height: 0, curve: 0, intensity: 0, angle: 0,
                curveCut: 0, cutFromTop: this.emotions[dominantEmotion][eyeIndex]['cutFromTop'], edge: 0, cutInY: 0
            };
            for (const [emotion, weight] of Object.entries(normalizedEmotions)) {
                const emotionData = this.emotions[emotion][eyeIndex];
                for (const [prop, value] of Object.entries(emotionData)) {
                    if (prop !== 'cutFromTop') {
                        blendedEyeData[prop] += value * weight;
                    }
                }
            }
            return blendedEyeData;
        });
        this.transitionProgress = 0;
    }

    setLookAt(x, y) {
        this.lookAtCoords = { x, y };
        this.updateEyePositions();
    }

    lerp(start, end, t) {
        return start * (1 - t) + end * t;
    }

    lerpColor(a, b, amount) {
        const ar = a >> 16,
            ag = a >> 8 & 0xff,
            ab = a & 0xff,
            br = b >> 16,
            bg = b >> 8 & 0xff,
            bb = b & 0xff,
            rr = ar + amount * (br - ar),
            rg = ag + amount * (bg - ag),
            rb = ab + amount * (bb - ab);

        return (rr << 16) + (rg << 8) + (rb | 0);
    }

    isInsideEllipse(x, y, width, height, curveCut, cutFromTop) {
        const normalizedX = (x - width / 2) / (width / 2);
        const normalizedY = (y - height / 2) / (height / 2);
        const baseEllipse = (normalizedX * normalizedX + normalizedY * normalizedY) <= 1;

        if (curveCut > 0) {
            const cutY = cutFromTop ? -1 + curveCut : 1 - curveCut;
            const cutCurve = Math.sqrt(1 - normalizedX * normalizedX) * curveCut;
            const adjustedCutY = cutFromTop ? cutY + cutCurve : cutY - cutCurve;

            if (cutFromTop) {
                return baseEllipse && normalizedY > adjustedCutY;
            } else {
                return baseEllipse && normalizedY < adjustedCutY;
            }
        }

        return baseEllipse;
    }

    animate() {
        this.transitionProgress += 0.05;
        if (this.transitionProgress > 1) this.transitionProgress = 1;

        this.eyeContainers.forEach((container, eyeIndex) => {
            const currentEyeData = this.currentEyeData[eyeIndex];
            const targetEyeData = this.targetEyeData[eyeIndex];

            for (const prop in currentEyeData) {
                if (prop === 'cutFromTop') {
                    currentEyeData[prop] = targetEyeData[prop];
                } else {
                    currentEyeData[prop] = this.lerp(currentEyeData[prop], targetEyeData[prop], this.transitionProgress);
                }
            }

            container.rotation = currentEyeData.angle * Math.PI / 180;

            container.children.forEach((led, index) => {
                const x = index % this.maxWidth;
                const y = Math.floor(index / this.maxWidth);

                if (this.isInsideEllipse(x - (this.maxWidth - currentEyeData.width) / 2,
                    y - (this.maxHeight - currentEyeData.height) / 2,
                    currentEyeData.width, currentEyeData.height,
                    currentEyeData.curveCut, currentEyeData.cutFromTop)) {
                    led.visible = true;
                    const distanceFromCenter = Math.abs(x - this.maxWidth / 2) / (currentEyeData.width / 2);
                    const yOffset = currentEyeData.curve * distanceFromCenter * currentEyeData.height * 0.5;
                    led.y = y * (this.ledSize + this.ledSpacing) + yOffset;

                    // let brightness = Math.min(currentEyeData.intensity * (1 - this.blinkProgress), 1);
                    let brightness = Math.min(1.0 * (1 - this.blinkProgress), 1);

                    const distanceFromEdge = 1 - Math.sqrt(
                        ((x - (this.maxWidth - currentEyeData.width) / 2) - currentEyeData.width / 2) ** 2 / (currentEyeData.width ** 2 / 4) +
                        ((y - (this.maxHeight - currentEyeData.height) / 2) - currentEyeData.height / 2) ** 2 / (currentEyeData.height ** 2 / 4)
                    );

                    if (distanceFromEdge < currentEyeData.edge) {
                        const colorFactor = Math.pow(distanceFromEdge, 0);
                        const ledColor = this.lerpColor(this.edgeColor, this.centerColor, colorFactor);
                        const finalColor = this.lerpColor(0xFFFFFF, ledColor, brightness);
                        led.tint = finalColor;

                        const shadowFactor = (currentEyeData.edge - distanceFromEdge) / currentEyeData.edge;
                        brightness *= (1 - shadowFactor);
                        led.alpha = brightness;
                    } else {
                        led.tint = PIXI.utils.rgb2hex([brightness, brightness, 1]);
                        led.alpha = brightness;
                    }

                    if (y < (this.maxHeight * currentEyeData.cutInY)) { led.visible = false; }
                } else {
                    led.visible = false;
                }
            });
        });

        if (this.transitionProgress === 1) {
            this.currentEmotion = this.targetEmotion;
        }

        const currentTime = Date.now();
        if (this.blinkProgress === 0) { this.blinkInterval = 3000 + (Math.random() * 3000 - 1000) }
        if (currentTime - this.lastBlinkTime > this.blinkInterval) {
            this.blinkProgress = Math.min(this.blinkProgress + 0.2, 1);
            if (this.blinkProgress === 1) {
                this.lastBlinkTime = currentTime;
                if (Math.random() < 0.3) { this.blinkAgain = true; }
            }
        } else {
            this.blinkProgress = Math.max(this.blinkProgress - 0.2, 0);
            if (this.blinkProgress === 0 & this.blinkAgain) {
                this.lastBlinkTime = currentTime - this.blinkInterval;
                this.blinkAgain = false
            }
        }
    }
}

const eveLEDAnimator = new EVELEDAnimator('eve-container');
eveLEDAnimator.setLookAt(0.5, 0.5);

// Runtime

const script = document.createElement('script');
script.src = '/scripts/face-api.min.js';
document.head.appendChild(script);

script.onload = () => {
    const video = document.createElement('video');
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    // Object to store emotion data between updates
    let emotionData = {
        happy: [],
        sad: [],
        angry: [],
        disgusted: [],
        surprised: [],
        fearful: [],
        neutral: []
    };

    let emotionBox = {
        happy: { canvas: null, score: 0 },
        sad: { canvas: null, score: 0 },
        angry: { canvas: null, score: 0 },
        disgusted: { canvas: null, score: 0 },
        surprised: { canvas: null, score: 0 },
        fearful: { canvas: null, score: 0 },
        neutral: { canvas: null, score: 0 }
    };

    let lastUpdateTime = 0;
    let nextUpdateInterval = getRandomInterval(1500, 4000);

    navigator.mediaDevices.getUserMedia({
        video: {
            facingMode: "user",
            width: { ideal: 1280 },
            height: { ideal: 720 }
        }
    })
        .then(stream => {
            video.srcObject = stream;
            video.play();
        })
        .catch(err => {
            console.error("Error accessing the webcam", err);
        });

    Promise.all([
        faceapi.nets.tinyFaceDetector.loadFromUri('/models'),
        faceapi.nets.faceLandmark68Net.loadFromUri('/models'),
        faceapi.nets.faceRecognitionNet.loadFromUri('/models'),
        faceapi.nets.faceExpressionNet.loadFromUri('/models')
    ]).then(startVideoProcessing);

    function updateDisplayedEmotion() {
        const averageEmotions = {};
        let dominantEmotion = '';
        let maxAverage = -1;

        // Calculate average for each emotion
        for (let emotion in emotionData) {
            if (emotionData[emotion].length > 0) {
                const sum = emotionData[emotion].reduce((a, b) => a + b, 0);
                const avg = sum / emotionData[emotion].length;
                averageEmotions[emotion] = avg;

                // Determine dominant emotion
                if (avg > maxAverage) {
                    maxAverage = avg;
                    dominantEmotion = emotion;
                }
            } else {
                averageEmotions[emotion] = 0;
            }
        }

        if (dominantEmotion) {
            eveLEDAnimator.setEmotions(averageEmotions, dominantEmotion);

            if (emotionBox[dominantEmotion].canvas) {
                emotionBox[dominantEmotion].canvas.toBlob(blob => {
                    const formData = new FormData();
                    formData.append('image', blob, 'face.jpg');
                    fetch('/save_emotion/' + dominantEmotion, {
                        method: 'POST',
                        body: formData
                    });
                }, 'image/jpeg');
            }

            for (let emotion in emotionData) {
                emotionData[emotion] = [];
            }

            for (let emotion in emotionBox) {
                emotionBox[emotion] = { canvas: null, score: 0 };
            }
        }
    }

    function startVideoProcessing() {
        const captureAndProcessFrame = async () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
                .withFaceLandmarks()
                .withFaceExpressions();

            if (detections.length > 0) {
                const face = detections[0];
                const { box } = face.detection;
                const expressions = face.expressions;

                for (let emotion in emotionData) {
                    if (expressions[emotion] > 0.9) {
                        emotionData[emotion].push(expressions[emotion]);

                        if (expressions[emotion] > emotionBox[emotion].score) {
                            const margin = 50;
                            const faceCanvas = document.createElement('canvas');
                            const faceCtx = faceCanvas.getContext('2d');
                            faceCanvas.width = box.width + 2 * margin;
                            faceCanvas.height = box.height + 2 * margin;
                            faceCtx.drawImage(
                                canvas,
                                box.x - margin, box.y - margin,
                                box.width + 2 * margin, box.height + 2 * margin,
                                0, 0,
                                faceCanvas.width, faceCanvas.height
                            );

                            emotionBox[emotion] = {
                                canvas: faceCanvas,
                                score: expressions[emotion]
                            };
                        }
                    }
                }

                const currentTime = Date.now();
                if (currentTime - lastUpdateTime >= nextUpdateInterval) {
                    dominantEmotion = updateDisplayedEmotion();
                    lastUpdateTime = currentTime;
                    nextUpdateInterval = getRandomInterval(1500, 4000);
                }
            } else {
                console.log('No face detected');
            }
        };

        if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
            setInterval(captureAndProcessFrame, 500);
        } else {
            setInterval(captureAndProcessFrame, 250);
        }
    }
};
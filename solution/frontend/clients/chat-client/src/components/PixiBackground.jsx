import React, { useEffect, useRef } from 'react';
import { Application, Container, Graphics, utils } from 'pixi.js';

// Create a PixiBackground component
const PixiBackground = () => {
    const pixiContainerRef = useRef(null);

    const getRandomInterval = (min, max) => {
        min = Math.ceil(min);
        max = Math.floor(max);
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    useEffect(() => {
        if (!pixiContainerRef.current) return;

        // Create Pixi application
        const app = new Application({
            resizeTo: window,
            backgroundColor: 0xFFFFFF,
            antialias: true,
        });

        // Add the Pixi canvas to our container
        pixiContainerRef.current.appendChild(app.view);

        // Your original Pixi.js code goes here
        const BASE_WIDTH = 2048;
        const BASE_HEIGHT = 1200;
        const BASE_RATIO = BASE_WIDTH / BASE_HEIGHT
        const EYE_DISTANCE_RATIO = 0.42;

        const physicalWidth = window.innerWidth;
        const physicalHeight = window.innerHeight;

        let physicalRatio = physicalWidth / physicalHeight
        let scaleFactor = Math.max(physicalWidth / BASE_WIDTH, physicalHeight / BASE_HEIGHT) * (physicalRatio / BASE_RATIO);
        let letSizeBase = 8;

        if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
            let alpha = 1.0 - ((physicalWidth - physicalHeight) / physicalWidth) ** 2;
            physicalRatio = physicalWidth / physicalHeight
            scaleFactor = Math.max(physicalHeight / BASE_WIDTH, physicalWidth / BASE_HEIGHT) * (physicalRatio / BASE_RATIO) * alpha;
            letSizeBase = 12;
            screen.orientation.lock('landscape');
        }

        const ledSize = letSizeBase * scaleFactor;
        const ledSpacing = 1 * scaleFactor;

        const eyesContainer = new Container();
        app.stage.addChild(eyesContainer);

        const eyeContainers = [new Container(), new Container()];
        eyeContainers.forEach(container => eyesContainer.addChild(container));

        let currentEmotion = 'neutral';
        let targetEmotion = 'neutral';
        let transitionProgress = 1;
        let lookAtCoords = { x: 0.5, y: 0.5 };

        const updateEyePositions = () => {
            const x = lookAtCoords.x * app.screen.width;
            const y = lookAtCoords.y * app.screen.height;
            eyesContainer.position.set(x, y);
        }

        const resize = () => {
            app.renderer.resize(window.innerWidth, window.innerHeight);
            updateEyePositions();
        }

        window.addEventListener('resize', resize);
        
        const emotions = {
            neutral: [
                { width: Math.floor(50 * scaleFactor), height: Math.floor(30 * scaleFactor), curve: 0, intensity: 0.85, angle: 8, curveCut: 0, cutFromTop: false, edge: 0.16, cutInY: 0.0 },
                { width: Math.floor(50 * scaleFactor), height: Math.floor(30 * scaleFactor), curve: 0, intensity: 0.85, angle: -8, curveCut: 0, cutFromTop: false, edge: 0.16, cutInY: 0.0 }
            ],
            joy: [
                { width: Math.floor(40 * scaleFactor), height: Math.floor(40 * scaleFactor), curve: 0, intensity: 1.0, angle: 0, curveCut: 0.7, cutFromTop: false, edge: 0.08, cutInY: 0.0 },
                { width: Math.floor(40 * scaleFactor), height: Math.floor(40 * scaleFactor), curve: 0, intensity: 1.0, angle: 0, curveCut: 0.7, cutFromTop: false, edge: 0.08, cutInY: 0.0 }
            ],
            sadness: [
                { width: Math.floor(45 * scaleFactor), height: Math.floor(40 * scaleFactor), curve: -0.2, intensity: 0.7, angle: -8, curveCut: 0.5, cutFromTop: false, edge: 0.32, cutInY: 0.20 },
                { width: Math.floor(45 * scaleFactor), height: Math.floor(40 * scaleFactor), curve: -0.2, intensity: 0.7, angle: 8, curveCut: 0.5, cutFromTop: false, edge: 0.32, cutInY: 0.20 }
            ],
            anger: [
                { width: Math.floor(45 * scaleFactor), height: Math.floor(22.5 * scaleFactor), curve: -0.3, intensity: 1.0, angle: 16, curveCut: 0.5, cutFromTop: true, edge: 0.24, cutInY: 0.0 },
                { width: Math.floor(45 * scaleFactor), height: Math.floor(22.5 * scaleFactor), curve: -0.3, intensity: 1.0, angle: -16, curveCut: 0.5, cutFromTop: true, edge: 0.24, cutInY: 0.0 }
            ],
            surprise: [
                { width: Math.floor(40 * scaleFactor), height: Math.floor(40 * scaleFactor), curve: 0, intensity: 1.0, angle: 0, curveCut: 0, cutFromTop: false, edge: 0.08, cutInY: 0.0 },
                { width: Math.floor(40 * scaleFactor), height: Math.floor(40 * scaleFactor), curve: 0, intensity: 1.0, angle: 0, curveCut: 0, cutFromTop: false, edge: 0.08, cutInY: 0.0 }
            ],
            fear: [
                { width: Math.floor(30 * scaleFactor), height: Math.floor(30 * scaleFactor), curve: 0, intensity: 0.7, angle: -16, curveCut: 0.3, cutFromTop: true, edge: 0.32, cutInY: 0.0 },
                { width: Math.floor(30 * scaleFactor), height: Math.floor(30 * scaleFactor), curve: 0, intensity: 0.7, angle: 16, curveCut: 0.3, cutFromTop: true, edge: 0.32, cutInY: 0.0 }
            ],
            disgust: [
                { width: Math.floor(50 * scaleFactor), height: Math.floor(40 * scaleFactor), curve: 0, intensity: 0.7, angle: -24, curveCut: 0.5, cutFromTop: true, edge: 0.24, cutInY: 0.0 },
                { width: Math.floor(50 * scaleFactor), height: Math.floor(40 * scaleFactor), curve: 0, intensity: 0.7, angle: -8, curveCut: 0.5, cutFromTop: true, edge: 0.24, cutInY: 0.0 }
            ]
        };

        const createLEDEyes = () => {
            eyeContainers.forEach((container, index) => {
                const totalWidth = (ledSize + ledSpacing) * maxWidth;
                const totalHeight = (ledSize + ledSpacing) * maxHeight;

                for (let y = 0; y < maxHeight; y++) {
                    for (let x = 0; x < maxWidth; x++) {
                        const led = new Graphics();
                        led.beginFill(0xFE007A);
                        led.drawRect(0, 0, ledSize, ledSize);
                        led.endFill();
                        led.x = x * (ledSize + ledSpacing);
                        led.y = y * (ledSize + ledSpacing);
                        container.addChild(led);
                    }
                }

                container.pivot.x = totalWidth / 2;
                container.pivot.y = totalHeight / 2;
            });

            const eyeDistance = Math.max(app.screen.width, app.screen.height) * EYE_DISTANCE_RATIO;
            eyeContainers[0].x = -eyeDistance / 2;
            eyeContainers[1].x = eyeDistance / 2;
        }

        let currentEyesData = JSON.parse(JSON.stringify(emotions.neutral));
        let targetEyesData = JSON.parse(JSON.stringify(emotions.neutral));

        const maxWidth = Math.max(...Object.values(emotions).flatMap(e => e.map(eye => eye.width)));
        const maxHeight = Math.max(...Object.values(emotions).flatMap(e => e.map(eye => eye.height)));
        createLEDEyes();

        let blinkProgress = 0;
        let blinkInterval = getRandomInterval(4000, 10000);
        let lastBlinkTime = Date.now();
        let blinkAgain = false;

        app.ticker.add(() => animate());
        resize();

        let centerColor = 0xFE007A;
        let edgeColor = 0xFFFFFF;

        const setEmotion = (dominantEmotion) => {
            targetEyesData = currentEyesData.map((_, eyeIndex) => {
                const blendedEyeData = {
                    width: 0, height: 0, curve: 0, intensity: 0, angle: 0,
                    curveCut: 0, cutFromTop: emotions[dominantEmotion][eyeIndex]['cutFromTop'], edge: 0, cutInY: 0
                };
                const emotionData = emotions[dominantEmotion][eyeIndex];
                for (const [prop, value] of Object.entries(emotionData)) {
                    if (prop !== 'cutFromTop') {
                        blendedEyeData[prop] += value;
                    }
                }
                return blendedEyeData;
            });
            targetEmotion = dominantEmotion;
            transitionProgress = 0;
        }
        window.setEmotion = setEmotion;

        const setLookAt = (x, y) => {
            lookAtCoords = { x, y };
            updateEyePositions();
        }
        window.setLookAt = setLookAt;

        const lerp = (start, end, t) => {
            return start * (1 - t) + end * t;
        }

        const lerpColor = (a, b, amount) => {
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

        const isInsideEllipse = (x, y, width, height, curveCut, cutFromTop) => {
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

        const animate = () => {
            transitionProgress += 0.05;
            if (transitionProgress > 1) transitionProgress = 1;

            eyeContainers.forEach((container, eyeIndex) => {
                const currentEyeData = currentEyesData[eyeIndex];
                const targetEyeData = targetEyesData[eyeIndex];

                for (const prop in currentEyeData) {
                    if (prop === 'cutFromTop') {
                        currentEyeData[prop] = targetEyeData[prop];
                    } else {
                        currentEyeData[prop] = lerp(currentEyeData[prop], targetEyeData[prop], transitionProgress);
                    }
                }

                container.rotation = currentEyeData.angle * Math.PI / 180;

                container.children.forEach((led, index) => {
                    const x = index % maxWidth;
                    const y = Math.floor(index / maxWidth);

                    if (isInsideEllipse(x - (maxWidth - currentEyeData.width) / 2,
                        y - (maxHeight - currentEyeData.height) / 2,
                        currentEyeData.width, currentEyeData.height,
                        currentEyeData.curveCut, currentEyeData.cutFromTop)) {
                        led.visible = true;
                        const distanceFromCenter = Math.abs(x - maxWidth / 2) / (currentEyeData.width / 2);
                        const yOffset = currentEyeData.curve * distanceFromCenter * currentEyeData.height * 0.5;
                        led.y = y * (ledSize + ledSpacing) + yOffset;

                        // let brightness = Math.min(currentEyeData.intensity * (1 - blinkProgress), 1);
                        let brightness = Math.min(1.0 * (1 - blinkProgress), 1);

                        const distanceFromEdge = 1 - Math.sqrt(
                            ((x - (maxWidth - currentEyeData.width) / 2) - currentEyeData.width / 2) ** 2 / (currentEyeData.width ** 2 / 4) +
                            ((y - (maxHeight - currentEyeData.height) / 2) - currentEyeData.height / 2) ** 2 / (currentEyeData.height ** 2 / 4)
                        );

                        if (distanceFromEdge < currentEyeData.edge) {
                            const colorFactor = Math.pow(distanceFromEdge, 0);
                            const ledColor = lerpColor(edgeColor, centerColor, colorFactor);
                            const finalColor = lerpColor(0xFFFFFF, ledColor, brightness);
                            led.tint = finalColor;

                            const shadowFactor = (currentEyeData.edge - distanceFromEdge) / currentEyeData.edge;
                            brightness *= (1 - shadowFactor);
                            led.alpha = brightness;
                        } else {
                            led.tint = utils.rgb2hex([brightness, brightness, 1]);
                            led.alpha = brightness;
                        }

                        if (y < (maxHeight * currentEyeData.cutInY)) { led.visible = false; }
                    } else {
                        led.visible = false;
                    }
                });
            });

            if (transitionProgress === 1) {
                currentEmotion = targetEmotion;
            }

            const currentTime = Date.now();
            if (blinkProgress === 0) { blinkInterval = 3000 + (Math.random() * 3000 - 1000) }
            if (currentTime - lastBlinkTime > blinkInterval) {
                blinkProgress = Math.min(blinkProgress + 0.2, 1);
                if (blinkProgress === 1) {
                    lastBlinkTime = currentTime;
                    if (Math.random() < 0.3) { blinkAgain = true; }
                }
            } else {
                blinkProgress = Math.max(blinkProgress - 0.2, 0);
                if (blinkProgress === 0 & blinkAgain) {
                    lastBlinkTime = currentTime - blinkInterval;
                    blinkAgain = false
                }
            }
        }

        setLookAt(0.5, 0.42);

        // Cleanup
        return () => {
            window.removeEventListener('resize', resize);
            app.destroy(true);
        };
    }, []);

    return (
        <div
            ref={pixiContainerRef}
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                zIndex: 0
            }}
        />
    );
};

export default PixiBackground;
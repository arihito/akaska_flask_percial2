// ============================================================
// 決済ページ：クレジットカードスライダー背景エフェクト
// 構成: CardStreamController / PaymentParticleSystem(Three.js) / PaymentParticleScanner(Canvas)
// スキャナー位置・コンテナ幅は右カラム（paymentCardViewer）基準で計算
// ============================================================

// ============================================================
// カードスライダー（自動スクロールのみ）
// ============================================================
class CardStreamController {
    constructor() {
        this.viewer    = document.getElementById('paymentCardViewer');
        this.container = document.getElementById('paymentCardStream');
        this.cardLine  = document.getElementById('paymentCardLine');

        this.position     = 0;
        this.velocity     = 120;
        this.direction    = -1;
        this.isAnimating  = true;
        this.lastTime     = 0;
        this.minVelocity  = 120;
        this.containerWidth = 0;
        this.cardLineWidth  = 0;

        this.CARD_W = 340;
        this.CARD_H = 210;
        this.CARD_GAP = 40;

        this.init();
    }

    init() {
        this.populateCardLine();
        this.calculateDimensions();
        this.animate();
        this.startPeriodicUpdates();
        window.addEventListener('resize', () => this.calculateDimensions());
    }

    // 全幅を基準に計算
    calculateDimensions() {
        this.containerWidth = window.innerWidth;
        const cardCount     = this.cardLine.children.length;
        this.cardLineWidth  = (this.CARD_W + this.CARD_GAP) * cardCount;
    }

    // スキャナーX座標：右から40%（画面幅の60%）の位置
    getScannerX() {
        return window.innerWidth * 0.6;
    }

    animate() {
        const currentTime = performance.now();
        const deltaTime   = (currentTime - this.lastTime) / 1000;
        this.lastTime     = currentTime;

        if (this.isAnimating) {
            this.position += this.velocity * this.direction * deltaTime;
            this.updateCardPosition();
        }

        requestAnimationFrame(() => this.animate());
    }

    updateCardPosition() {
        const { containerWidth, cardLineWidth } = this;
        if (this.position < -cardLineWidth) {
            this.position = containerWidth;
        } else if (this.position > containerWidth) {
            this.position = -cardLineWidth;
        }
        this.cardLine.style.transform = `translateX(${this.position}px)`;
        this.updateCardClipping();
    }

    updateCardClipping() {
        const scannerX     = this.getScannerX();
        const scannerWidth = 8;
        const scannerLeft  = scannerX - scannerWidth / 2;
        const scannerRight = scannerX + scannerWidth / 2;
        let anyScanningActive = false;

        document.querySelectorAll('.payment-bg-card-wrapper').forEach((wrapper) => {
            const rect       = wrapper.getBoundingClientRect();
            const cardLeft   = rect.left;
            const cardRight  = rect.right;
            const cardWidth  = rect.width;
            const normalCard = wrapper.querySelector('.payment-bg-card-normal');
            const asciiCard  = wrapper.querySelector('.payment-bg-card-ascii');

            if (cardLeft < scannerRight && cardRight > scannerLeft) {
                anyScanningActive = true;
                const intersectLeft  = Math.max(scannerLeft - cardLeft, 0);
                const intersectRight = Math.min(scannerRight - cardLeft, cardWidth);

                normalCard.style.setProperty('--clip-right', `${(intersectLeft / cardWidth) * 100}%`);
                asciiCard.style.setProperty('--clip-left',   `${(intersectRight / cardWidth) * 100}%`);

                if (!wrapper.hasAttribute('data-scanned') && intersectLeft > 0) {
                    wrapper.setAttribute('data-scanned', 'true');
                    const scanEffect = document.createElement('div');
                    scanEffect.className = 'payment-bg-scan-effect';
                    wrapper.appendChild(scanEffect);
                    setTimeout(() => { scanEffect.remove(); }, 600);
                }
            } else {
                if (cardRight < scannerLeft) {
                    normalCard.style.setProperty('--clip-right', '100%');
                    asciiCard.style.setProperty('--clip-left',   '100%');
                } else if (cardLeft > scannerRight) {
                    normalCard.style.setProperty('--clip-right', '0%');
                    asciiCard.style.setProperty('--clip-left',   '0%');
                }
                wrapper.removeAttribute('data-scanned');
            }
        });

        if (window.paymentSetScannerScanning) {
            window.paymentSetScannerScanning(anyScanningActive);
        }
    }

    generateCode(width, height) {
        const randInt = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
        const pick    = (arr) => arr[randInt(0, arr.length - 1)];

        const lines = [
            '// compiled preview • scanner demo',
            '/* generated for visual effect – not executed */',
            'const SCAN_WIDTH = 8;', 'const FADE_ZONE = 35;',
            'const MAX_PARTICLES = 2500;', 'const TRANSITION = 0.05;',
            'function clamp(n,a,b){return Math.max(a,Math.min(b,n));}',
            'function lerp(a,b,t){return a+(b-a)*t;}',
            'const now = () => performance.now();',
            'const scanner = { x: Math.floor(window.innerWidth/2), width: SCAN_WIDTH, glow: 3.5 };',
            'function tick(t){ requestAnimationFrame(tick); const dt=0.016; }',
            'const state = { intensity: 1.2, particles: MAX_PARTICLES };',
        ];
        for (let i = 0; i < 40; i++) {
            lines.push(`const v${i} = (${randInt(1,9)} + ${randInt(10,99)}) * 0.${randInt(1,9)};`);
        }

        let flow = lines.join(' ').replace(/\s+/g, ' ').trim();
        const totalChars = width * height;
        while (flow.length < totalChars + width) {
            flow += ' ' + pick(lines).replace(/\s+/g, ' ').trim();
        }

        let out = '';
        let offset = 0;
        for (let row = 0; row < height; row++) {
            let line = flow.slice(offset, offset + width);
            if (line.length < width) line += ' '.repeat(width - line.length);
            out += line + (row < height - 1 ? '\n' : '');
            offset += width;
        }
        return out;
    }

    createCardWrapper(index) {
        const cardImages = window.PAYMENT_CARD_IMAGES || [];
        const w = this.CARD_W;
        const h = this.CARD_H;

        const wrapper    = document.createElement('div');
        wrapper.className = 'payment-bg-card-wrapper';
        wrapper.style.width  = w + 'px';
        wrapper.style.height = h + 'px';

        // 通常カード（画像）
        const normalCard  = document.createElement('div');
        normalCard.className = 'payment-bg-card-normal';
        normalCard.style.width  = w + 'px';
        normalCard.style.height = h + 'px';
        const cardImage   = document.createElement('img');
        cardImage.className = 'payment-bg-card-image';
        cardImage.src     = cardImages[index % cardImages.length] || '';
        cardImage.alt     = 'Credit Card';
        cardImage.onerror = () => {
            const canvas = document.createElement('canvas');
            canvas.width = w; canvas.height = h;
            const ctx  = canvas.getContext('2d');
            const grad = ctx.createLinearGradient(0, 0, w, h);
            grad.addColorStop(0, '#223344');
            grad.addColorStop(1, '#334455');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, w, h);
            cardImage.src = canvas.toDataURL();
        };
        normalCard.appendChild(cardImage);

        // ASCIIカード
        const asciiCard    = document.createElement('div');
        asciiCard.className = 'payment-bg-card-ascii';
        asciiCard.style.width  = w + 'px';
        asciiCard.style.height = h + 'px';
        const asciiContent  = document.createElement('div');
        asciiContent.className = 'payment-bg-ascii-content';
        const fontSize   = 10;
        const lineHeight = 12;
        const charWidth  = 6;
        const codeWidth  = Math.floor(w / charWidth);
        const codeHeight = Math.floor(h / lineHeight);
        asciiContent.style.fontSize   = fontSize + 'px';
        asciiContent.style.lineHeight = lineHeight + 'px';
        asciiContent.textContent      = this.generateCode(codeWidth, codeHeight);
        asciiCard.appendChild(asciiContent);

        wrapper.appendChild(normalCard);
        wrapper.appendChild(asciiCard);
        return wrapper;
    }

    populateCardLine() {
        this.cardLine.innerHTML = '';
        for (let i = 0; i < 30; i++) {
            this.cardLine.appendChild(this.createCardWrapper(i));
        }
    }

    startPeriodicUpdates() {
        setInterval(() => {
            document.querySelectorAll('.payment-bg-ascii-content').forEach((el) => {
                if (Math.random() < 0.15) {
                    const cw = Math.floor(this.CARD_W / 6);
                    const ch = Math.floor(this.CARD_H / 12);
                    el.textContent = this.generateCode(cw, ch);
                }
            });
        }, 200);

        const updateClipping = () => {
            this.updateCardClipping();
            requestAnimationFrame(updateClipping);
        };
        updateClipping();
    }
}

// ============================================================
// パーティクルシステム（Three.js）- 右カラム内
// ============================================================
class PaymentParticleSystem {
    constructor(viewer) {
        this.viewer        = viewer;
        this.canvas        = document.getElementById('paymentParticleCanvas');
        this.particleCount = 300;
        this.scene = null; this.camera = null;
        this.renderer = null; this.particles = null;
        this.velocities = null; this.alphas = null;

        if (!window.THREE || !this.canvas) return;
        this.init();
    }

    getSize() {
        return { w: window.innerWidth, h: 250 };
    }

    init() {
        const { w, h } = this.getSize();
        this.scene  = new THREE.Scene();
        this.camera = new THREE.OrthographicCamera(-w / 2, w / 2, h / 2, -h / 2, 1, 1000);
        this.camera.position.z = 100;

        this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, alpha: true, antialias: true });
        this.renderer.setSize(w, h);
        this.renderer.setClearColor(0x000000, 0);
        // CSS競合を防ぐためインラインで明示
        this.canvas.style.width  = w + 'px';
        this.canvas.style.height = h + 'px';

        this.createParticles(w, h);
        this.animate();
        window.addEventListener('resize', () => this.onResize());
    }

    createParticles(w, h) {
        const geometry   = new THREE.BufferGeometry();
        const positions  = new Float32Array(this.particleCount * 3);
        const colors     = new Float32Array(this.particleCount * 3);
        const sizes      = new Float32Array(this.particleCount);
        const velocities = new Float32Array(this.particleCount);

        const texCanvas = document.createElement('canvas');
        texCanvas.width = texCanvas.height = 100;
        const ctx  = texCanvas.getContext('2d');
        const half = 50;
        const grad = ctx.createRadialGradient(half, half, 0, half, half, half);
        grad.addColorStop(0.025, '#fff');
        grad.addColorStop(0.1,   'hsl(217, 61%, 33%)');
        grad.addColorStop(0.25,  'hsl(217, 64%, 6%)');
        grad.addColorStop(1,     'transparent');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(half, half, half, 0, Math.PI * 2);
        ctx.fill();
        const texture = new THREE.CanvasTexture(texCanvas);

        for (let i = 0; i < this.particleCount; i++) {
            positions[i * 3]     = (Math.random() - 0.5) * w * 2;
            positions[i * 3 + 1] = (Math.random() - 0.5) * h;
            positions[i * 3 + 2] = 0;
            colors[i * 3] = colors[i * 3 + 1] = colors[i * 3 + 2] = 1;
            sizes[i]      = (Math.random() * 140 + 60) / 8;
            velocities[i] = Math.random() * 60 + 30;
        }
        this.velocities = velocities;
        this.particleW  = w;
        this.particleH  = h;

        const alphas = new Float32Array(this.particleCount);
        for (let i = 0; i < this.particleCount; i++) alphas[i] = (Math.random() * 8 + 2) / 10;
        this.alphas = alphas;

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color',    new THREE.BufferAttribute(colors,    3));
        geometry.setAttribute('size',     new THREE.BufferAttribute(sizes,     1));
        geometry.setAttribute('alpha',    new THREE.BufferAttribute(alphas,    1));

        const material = new THREE.ShaderMaterial({
            uniforms: { pointTexture: { value: texture }, size: { value: 15.0 } },
            vertexShader: `
                attribute float alpha; varying float vAlpha; varying vec3 vColor; uniform float size;
                void main() {
                    vAlpha = alpha; vColor = color;
                    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
                    gl_PointSize = size;
                    gl_Position = projectionMatrix * mvPosition;
                }
            `,
            fragmentShader: `
                uniform sampler2D pointTexture; varying float vAlpha; varying vec3 vColor;
                void main() {
                    gl_FragColor = vec4(vColor, vAlpha) * texture2D(pointTexture, gl_PointCoord);
                }
            `,
            transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, vertexColors: true,
        });

        this.particles = new THREE.Points(geometry, material);
        this.scene.add(this.particles);
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        if (!this.particles) return;

        const positions = this.particles.geometry.attributes.position.array;
        const alphas    = this.particles.geometry.attributes.alpha.array;
        const time      = Date.now() * 0.001;
        const halfW     = (this.particleW || 400) / 2;

        for (let i = 0; i < this.particleCount; i++) {
            positions[i * 3] += this.velocities[i] * 0.016;
            if (positions[i * 3] > halfW + 100) {
                positions[i * 3]     = -halfW - 100;
                positions[i * 3 + 1] = (Math.random() - 0.5) * (this.particleH || 250);
            }
            positions[i * 3 + 1] += Math.sin(time + i * 0.1) * 0.5;
            const twinkle = Math.floor(Math.random() * 10);
            if (twinkle === 1 && alphas[i] > 0) alphas[i] -= 0.05;
            else if (twinkle === 2 && alphas[i] < 1) alphas[i] += 0.05;
            alphas[i] = Math.max(0, Math.min(1, alphas[i]));
        }
        this.particles.geometry.attributes.position.needsUpdate = true;
        this.particles.geometry.attributes.alpha.needsUpdate    = true;
        this.renderer.render(this.scene, this.camera);
    }

    onResize() {
        const { w, h } = this.getSize();
        this.camera.left  = -w / 2; this.camera.right = w / 2;
        this.camera.top   = h / 2;  this.camera.bottom = -h / 2;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(w, h);
        this.particleW = w; this.particleH = h;
    }
}

// ============================================================
// スキャナーパーティクル（Canvas 2D）- 右カラム内
// ============================================================
class PaymentParticleScanner {
    constructor(viewer) {
        this.viewer = viewer;
        this.canvas = document.getElementById('paymentScannerCanvas');
        this.ctx    = this.canvas.getContext('2d');

        this.w = window.innerWidth;
        this.h = 300;
        this.particles        = [];
        this.count            = 0;
        this.maxParticles     = 600;
        this.intensity        = 0.8;
        this.lightBarX        = this.w * 0.44;
        this.lightBarWidth    = 3;
        this.fadeZone         = 60;

        this.scanTargetIntensity  = 1.8;
        this.scanTargetParticles  = 2000;
        this.scanTargetFadeZone   = 35;

        this.scanningActive       = false;
        this.baseIntensity        = this.intensity;
        this.baseMaxParticles     = this.maxParticles;
        this.baseFadeZone         = this.fadeZone;
        this.currentIntensity     = this.intensity;
        this.currentMaxParticles  = this.maxParticles;
        this.currentFadeZone      = this.fadeZone;
        this.currentGlowIntensity = 1;
        this.transitionSpeed      = 0.05;

        this.setupCanvas();
        this.createGradientCache();
        this.initParticles();
        this.animate();
        window.addEventListener('resize', () => this.onResize());

        window.paymentSetScannerScanning = (active) => { this.scanningActive = active; };
    }

    setupCanvas() {
        this.canvas.width        = this.w;
        this.canvas.height       = this.h;
        this.canvas.style.width  = this.w + 'px';
        this.canvas.style.height = this.h + 'px';
        this.ctx.clearRect(0, 0, this.w, this.h);
    }

    onResize() {
        this.w = window.innerWidth;
        this.lightBarX = this.w * 0.60;
        this.setupCanvas();
    }

    createGradientCache() {
        this.gradientCanvas = document.createElement('canvas');
        this.gradientCanvas.width = this.gradientCanvas.height = 16;
        const gCtx = this.gradientCanvas.getContext('2d');
        const half = 8;
        const grad = gCtx.createRadialGradient(half, half, 0, half, half, half);
        grad.addColorStop(0,   'rgba(255,255,255,1)');
        grad.addColorStop(0.3, 'rgba(196,181,253,0.8)');
        grad.addColorStop(0.7, 'rgba(139,92,246,0.4)');
        grad.addColorStop(1,   'transparent');
        gCtx.fillStyle = grad;
        gCtx.beginPath();
        gCtx.arc(half, half, half, 0, Math.PI * 2);
        gCtx.fill();
    }

    randomFloat(min, max) { return Math.random() * (max - min) + min; }

    createParticle() {
        const ratio = this.intensity / this.baseIntensity;
        const sm    = 1 + (ratio - 1) * 1.2;
        return {
            x:             this.lightBarX + this.randomFloat(-this.lightBarWidth / 2, this.lightBarWidth / 2),
            y:             this.randomFloat(0, this.h),
            vx:            this.randomFloat(0.2, 1.0) * sm,
            vy:            this.randomFloat(-0.15, 0.15) * sm,
            radius:        this.randomFloat(0.4, 1) * (1 + (ratio - 1) * 0.7),
            alpha:         this.randomFloat(0.6, 1),
            decay:         this.randomFloat(0.005, 0.025) * (2 - ratio * 0.5),
            originalAlpha: 0,
            life:          1.0,
            time:          0,
            twinkleSpeed:  this.randomFloat(0.02, 0.08) * sm,
            twinkleAmount: this.randomFloat(0.1, 0.25),
        };
    }

    initParticles() {
        for (let i = 0; i < this.maxParticles; i++) {
            const p = this.createParticle();
            p.originalAlpha = p.alpha;
            this.count++;
            this.particles[this.count] = p;
        }
    }

    updateParticle(p) {
        p.x += p.vx; p.y += p.vy; p.time++;
        p.alpha = p.originalAlpha * p.life + Math.sin(p.time * p.twinkleSpeed) * p.twinkleAmount;
        p.life -= p.decay;
        if (p.x > this.w + 10 || p.life <= 0) this.resetParticle(p);
    }

    resetParticle(p) {
        p.x = this.lightBarX + this.randomFloat(-this.lightBarWidth / 2, this.lightBarWidth / 2);
        p.y = this.randomFloat(0, this.h);
        p.vx = this.randomFloat(0.2, 1.0);
        p.vy = this.randomFloat(-0.15, 0.15);
        p.alpha = this.randomFloat(0.6, 1);
        p.originalAlpha = p.alpha;
        p.life = 1.0; p.time = 0;
    }

    drawParticle(p) {
        if (p.life <= 0) return;
        let fadeAlpha = 1;
        if (p.y < this.fadeZone) fadeAlpha = p.y / this.fadeZone;
        else if (p.y > this.h - this.fadeZone) fadeAlpha = (this.h - p.y) / this.fadeZone;
        fadeAlpha = Math.max(0, Math.min(1, fadeAlpha));
        this.ctx.globalAlpha = p.alpha * fadeAlpha;
        this.ctx.drawImage(this.gradientCanvas, p.x - p.radius, p.y - p.radius, p.radius * 2, p.radius * 2);
    }

    drawLightBar() {
        const vertGrad = this.ctx.createLinearGradient(0, 0, 0, this.h);
        vertGrad.addColorStop(0,                      'rgba(255,255,255,0)');
        vertGrad.addColorStop(this.fadeZone / this.h, 'rgba(255,255,255,1)');
        vertGrad.addColorStop(1 - this.fadeZone / this.h, 'rgba(255,255,255,1)');
        vertGrad.addColorStop(1,                      'rgba(255,255,255,0)');

        this.ctx.globalCompositeOperation = 'lighter';

        const target = this.scanningActive ? 3.5 : 1;
        this.currentGlowIntensity += (target - this.currentGlowIntensity) * this.transitionSpeed;
        const g  = this.currentGlowIntensity;
        const lw = this.lightBarWidth;
        const x  = this.lightBarX;

        const drawRect = (halfW, color) => {
            const grd = this.ctx.createLinearGradient(x - halfW, 0, x + halfW, 0);
            grd.addColorStop(0,   'rgba(0,0,0,0)');
            grd.addColorStop(0.5, color);
            grd.addColorStop(1,   'rgba(0,0,0,0)');
            this.ctx.fillStyle = grd;
            this.ctx.fillRect(x - halfW, 0, halfW * 2, this.h);
        };

        this.ctx.globalAlpha = 1;
        drawRect(lw,     `rgba(255,255,255,${g})`);
        this.ctx.globalAlpha = this.scanningActive ? 1.0 : 0.8;
        drawRect(lw * 2, `rgba(196,181,253,${0.8 * g})`);
        this.ctx.globalAlpha = this.scanningActive ? 0.8 : 0.6;
        drawRect(lw * 4, `rgba(139,92,246,${0.4 * g})`);

        if (this.scanningActive) {
            this.ctx.globalAlpha = 0.6;
            drawRect(lw * 8, 'rgba(139,92,246,0.2)');
        }

        this.ctx.globalCompositeOperation = 'destination-in';
        this.ctx.globalAlpha = 1;
        this.ctx.fillStyle   = vertGrad;
        this.ctx.fillRect(0, 0, this.w, this.h);
    }

    render() {
        const ti  = this.scanningActive ? this.scanTargetIntensity  : this.baseIntensity;
        const tp  = this.scanningActive ? this.scanTargetParticles  : this.baseMaxParticles;
        const tfz = this.scanningActive ? this.scanTargetFadeZone   : this.baseFadeZone;

        this.currentIntensity    += (ti  - this.currentIntensity)    * this.transitionSpeed;
        this.currentMaxParticles += (tp  - this.currentMaxParticles) * this.transitionSpeed;
        this.currentFadeZone     += (tfz - this.currentFadeZone)     * this.transitionSpeed;

        this.intensity    = this.currentIntensity;
        this.maxParticles = Math.floor(this.currentMaxParticles);
        this.fadeZone     = this.currentFadeZone;

        this.ctx.globalCompositeOperation = 'source-over';
        this.ctx.clearRect(0, 0, this.w, this.h);
        this.drawLightBar();

        this.ctx.globalCompositeOperation = 'lighter';
        for (let i = 1; i <= this.count; i++) {
            if (this.particles[i]) {
                this.updateParticle(this.particles[i]);
                this.drawParticle(this.particles[i]);
            }
        }

        const ratio = this.intensity / this.baseIntensity;
        const spawn = (threshold, mult) => {
            if (ratio > threshold && Math.random() < (ratio - threshold) * mult && this.count < this.maxParticles + 200) {
                const p = this.createParticle();
                p.originalAlpha = p.alpha;
                this.count++;
                this.particles[this.count] = p;
            }
        };
        if (Math.random() < this.intensity && this.count < this.maxParticles) {
            const p = this.createParticle();
            p.originalAlpha = p.alpha;
            this.count++;
            this.particles[this.count] = p;
        }
        spawn(1.1, 1.2); spawn(1.3, 1.4); spawn(1.5, 1.8); spawn(2.0, 2.0);

        if (this.count > this.maxParticles + 200) {
            const excess = Math.min(15, this.count - this.maxParticles);
            for (let i = 0; i < excess; i++) delete this.particles[this.count - i];
            this.count -= excess;
        }
    }

    animate() {
        this.render();
        requestAnimationFrame(() => this.animate());
    }
}

// ============================================================
// 初期化
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    const viewer = document.getElementById('paymentCardViewer');
    if (!viewer) return;

    new CardStreamController();
    new PaymentParticleSystem(viewer);
    new PaymentParticleScanner(viewer);
});

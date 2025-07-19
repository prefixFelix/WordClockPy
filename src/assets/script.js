
// ==========================================
// GLOBAL VARIABLES
// ==========================================
let originalConfig = {};
let currentLedType = 'RGBW';

// ==========================================
// CONFIGURATION MANAGEMENT
// ==========================================
const Config = {
    // Static configuration for debugging
    staticConfig: {
        version: '1.2',
        power: true,
        brightness: 1.0,
        color: [0, 0, 0, 255],
        led_type: 'RGBW',
        show_it_is: true,
        show_minutes: true,
        show_oclock: true,
        transition: null,
        transition_duration: 0.05,
        transition_smoothness: 0.0039,
        sleep: true,
        sleep_time: [1, 6],
        ota: true,
        gamma_correction: true,
        wifi_ssid: 'x',
        static_ip: false,
        ip: '192.168.0.111',
        subnet_mask: '255.255.255.0',
        gateway: '192.168.0.1',
        dns: '8.8.8.8'
    },

    async fetch() {
        try {
            const response = await fetch('/get_config');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const config = await response.json();
            originalConfig = { ...config };
            this.updateUI(config);
        } catch (error) {
            console.error('Error fetching configuration:', error);
            console.log('Using static configuration for debugging');
            originalConfig = { ...this.staticConfig };
            this.updateUI(this.staticConfig);
        }
    },

    updateUI(config) {
        // Store current LED type
        currentLedType = config.led_type;

        // Power toggle
        document.getElementById('power-toggle').checked = config.power;

        // Brightness
        const brightnessValue = Math.round(config.brightness * 100);
        document.getElementById('brightness-slider').value = brightnessValue;
        document.getElementById('brightness-value').textContent = brightnessValue;

        // Layout settings
        document.getElementById('show-it-is').checked = config.show_it_is;
        document.getElementById('show-minutes').checked = config.show_minutes;
        document.getElementById('show-oclock').checked = config.show_oclock !== undefined ? config.show_oclock : true;
        document.getElementById('minute-clockwise').checked = config.minute_clockwise !== undefined ? config.minute_clockwise : true;

        // Transition settings
        const transitionSelect = document.getElementById('transition-select');
        if (config.transition === 'concurrent_fade') {
            transitionSelect.value = 'concurrent_fade';
        } else if (config.transition === 'successive_fade') {
            transitionSelect.value = 'successive_fade';
        } else {
            transitionSelect.value = 'none';
        }
        document.getElementById('transition-duration').value = config.transition_duration || 0.05;
        document.getElementById('transition-smoothness').value = config.transition_smoothness || 0.0039;

        // Schedule settings
        document.getElementById('schedule-enabled').checked = config.sleep;
        if (config.sleep_time && Array.isArray(config.sleep_time) && config.sleep_time.length === 2) {
            document.getElementById('start-time').value = config.sleep_time[0];
            document.getElementById('end-time').value = config.sleep_time[1];
        }

        // Misc settings
        document.getElementById('ota-update').checked = config.ota !== undefined ? config.ota : false;
        document.getElementById('gamma-correction').checked = config.gamma_correction !== undefined ? config.gamma_correction : true;
        document.getElementById('wifi-ssid').value = config.wifi_ssid || '';
        // WiFi password is never populated from config for security
        
        // Static IP settings
        document.getElementById('static-ip').checked = config.static_ip !== undefined ? config.static_ip : false;
        document.getElementById('device-ip').value = config.ip || '';
        document.getElementById('subnet-mask').value = config.subnet_mask || '255.255.255.0';
        document.getElementById('gateway').value = config.gateway || '';
        document.getElementById('dns').value = config.dns || '8.8.8.8';

        // Handle color inputs and controls
        ColorInputs.update(config.led_type, config.color);
        ColorControls.update(config.led_type);
        
        // Update static IP fields state
        StaticIP.updateFields();
        
        // Initial color preview update
        ColorPreview.update();
        
        // Update version number
        if (config.version) {
            document.getElementById('version-number').textContent = config.version;
        }
    },

    async save() {
        const currentSettings = this.getCurrentSettings();
        const changedSettings = this.getChangedSettings(currentSettings);

        if (Object.keys(changedSettings).length === 0) {
            console.log('No changes detected.');
            return false;
        }

        try {
            const response = await fetch('/set_config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(changedSettings)
            });

            if (!response.ok) {
                throw new Error('Server responded with status: ' + response.status);
            }

            const data = await response.json();
            console.log('Success:', data);
            
            // Update original config to reflect new state
            Object.assign(originalConfig, changedSettings);
            return true;
        } catch (error) {
            console.error('Error:', error);
            throw error;
        }
    },

    getCurrentSettings() {
        const colorInputs = document.querySelectorAll('#color-inputs-container input[type="number"]');
        const colorValues = Array.from(colorInputs).map(input => parseInt(input.value));

        return {
            power: document.getElementById('power-toggle').checked,
            brightness: parseInt(document.getElementById('brightness-slider').value) / 100,
            color: colorValues,
            show_it_is: document.getElementById('show-it-is').checked,
            show_minutes: document.getElementById('show-minutes').checked,
            show_oclock: document.getElementById('show-oclock').checked,
            minute_clockwise: document.getElementById('minute-clockwise').checked,
            transition: document.getElementById('transition-select').value === 'none' ? null : document.getElementById('transition-select').value,
            transition_duration: parseFloat(document.getElementById('transition-duration').value),
            transition_smoothness: parseFloat(document.getElementById('transition-smoothness').value),
            sleep: document.getElementById('schedule-enabled').checked,
            sleep_time: [
                parseInt(document.getElementById('start-time').value),
                parseInt(document.getElementById('end-time').value)
            ],
            ota: document.getElementById('ota-update').checked,
            gamma_correction: document.getElementById('gamma-correction').checked,
            wifi_ssid: document.getElementById('wifi-ssid').value,
            wifi_passwd: document.getElementById('wifi-password').value,
            static_ip: document.getElementById('static-ip').checked,
            ip: document.getElementById('device-ip').value,
            subnet_mask: document.getElementById('subnet-mask').value,
            gateway: document.getElementById('gateway').value,
            dns: document.getElementById('dns').value
        };
    },

    getChangedSettings(currentSettings) {
        const changedSettings = {};
        const compareFields = [
            'power', 'brightness', 'show_it_is', 'show_minutes', 'show_oclock', 'minute_clockwise',
            'transition', 'transition_duration', 'transition_smoothness', 'sleep',
            'ota', 'gamma_correction', 'wifi_ssid', 'static_ip',
            'ip', 'subnet_mask', 'gateway', 'dns'
        ];

        // Compare simple fields
        compareFields.forEach(field => {
            if (currentSettings[field] !== originalConfig[field]) {
                changedSettings[field] = currentSettings[field];
            }
        });

        // Handle WiFi password separately - only include if user entered a value
        if (currentSettings.wifi_passwd && currentSettings.wifi_passwd.trim() !== '') {
            changedSettings.wifi_passwd = currentSettings.wifi_passwd;
        }

        // Compare color array
        if (this.arrayChanged(currentSettings.color, originalConfig.color)) {
            changedSettings.color = currentSettings.color;
        }

        // Compare sleep_time array
        if (this.arrayChanged(currentSettings.sleep_time, originalConfig.sleep_time)) {
            changedSettings.sleep_time = currentSettings.sleep_time;
        }

        return changedSettings;
    },

    arrayChanged(arr1, arr2) {
        if (!arr1 || !arr2) return true;
        if (arr1.length !== arr2.length) return true;
        return arr1.some((val, index) => val !== arr2[index]);
    }
};

// ==========================================
// COLOR MANAGEMENT
// ==========================================
const ColorInputs = {
    configurations: {
        'RGBW': [
            { label: 'R', color: '#ff5555', id: 'red-value' },
            { label: 'G', color: '#55ff55', id: 'green-value' },
            { label: 'B', color: '#5555ff', id: 'blue-value' },
            { label: 'W', color: '#dddddd', id: 'white-value' }
        ],
        'RGB': [
            { label: 'R', color: '#ff5555', id: 'red-value' },
            { label: 'G', color: '#55ff55', id: 'green-value' },
            { label: 'B', color: '#5555ff', id: 'blue-value' }
        ],
        'WWA': [
            { label: 'CW', color: '#88ccff', id: 'cold-value' },
            { label: 'NW', color: '#eeeeee', id: 'neutral-value' },
            { label: 'WW', color: '#ffaa00', id: 'warm-value' }
        ]
    },

    update(ledType, colorValues) {
        const container = document.getElementById('color-inputs-container');
        container.innerHTML = '';

        const colorConfig = this.configurations[ledType] || this.configurations['RGB'];

        colorConfig.forEach((config, index) => {
            const div = document.createElement('div');
            div.className = 'color-input';

            const label = document.createElement('div');
            label.className = 'color-label';
            label.style.color = config.color;
            label.textContent = config.label;

            const input = document.createElement('input');
            input.type = 'number';
            input.id = config.id;
            input.min = 0;
            input.max = 255;
            input.value = colorValues && colorValues[index] !== undefined ? colorValues[index] : 255;

            div.appendChild(label);
            div.appendChild(input);
            container.appendChild(div);
        });

        this.attachEventListeners();
    },

    attachEventListeners() {
        document.querySelectorAll('#color-inputs-container input[type="number"]').forEach(input => {
            input.addEventListener('input', function() {
                const min = parseInt(this.min);
                const max = parseInt(this.max);

                if (this.value === '') {
                    this.value = 0;
                } else if (parseInt(this.value) < min) {
                    this.value = min;
                } else if (parseInt(this.value) > max) {
                    this.value = max;
                }
                
                ColorPreview.update();
                
                // Update sliders when values change
                if (currentLedType === 'RGB' || currentLedType === 'RGBW') {
                    ColorSliders.updateFromRgb();
                } else if (currentLedType === 'WWA') {
                    ColorSliders.updateTempFromWwa();
                }
            });
        });
    }
};

const ColorControls = {
    update(ledType) {
        const colorPickerSection = document.getElementById('color-picker-section');
        const whiteContainer = document.getElementById('white-container');
        const tempContainer = document.getElementById('temp-container');

        if (ledType === 'RGB') {
            colorPickerSection.classList.remove('hidden');
            whiteContainer.classList.add('hidden');
            tempContainer.classList.add('hidden');
            this.initializeRgbSliders();
        } else if (ledType === 'RGBW') {
            colorPickerSection.classList.remove('hidden');
            whiteContainer.classList.remove('hidden');
            tempContainer.classList.add('hidden');
            this.initializeRgbSliders();
            this.initializeWhiteSlider();
        } else {
            colorPickerSection.classList.add('hidden');
            whiteContainer.classList.add('hidden');
            tempContainer.classList.remove('hidden');
        }
    },

    initializeRgbSliders() {
        const inputs = document.querySelectorAll('#color-inputs-container input[type="number"]');
        if (inputs.length >= 3) {
            const r = parseInt(inputs[0].value) || 255;
            const g = parseInt(inputs[1].value) || 255;
            const b = parseInt(inputs[2].value) || 255;
            
            const hsl = ColorUtils.rgbToHsl(r, g, b);
            document.getElementById('hue-slider').value = Math.round(hsl.h);
            
            let adjustedSaturation = hsl.s;
            if (hsl.l > 50) {
                adjustedSaturation = (100 - hsl.l) * 2;
            }
            
            document.getElementById('saturation-slider').value = Math.round(adjustedSaturation);
            document.getElementById('saturation-value').textContent = Math.round(adjustedSaturation);
            
            ColorSliders.updateSaturationGradient(hsl.h);
        }
    },

    initializeWhiteSlider() {
        const inputs = document.querySelectorAll('#color-inputs-container input[type="number"]');
        if (inputs.length >= 4) {
            const w = parseInt(inputs[3].value) || 0;
            document.getElementById('white-slider').value = w;
            document.getElementById('white-value').textContent = w;
        }
    }
};

const ColorSliders = {
    updateFromRgb() {
        const inputs = document.querySelectorAll('#color-inputs-container input[type="number"]');
        if (inputs.length < 3) return;

        const r = parseInt(inputs[0].value) || 0;
        const g = parseInt(inputs[1].value) || 0;
        const b = parseInt(inputs[2].value) || 0;

        const hsl = ColorUtils.rgbToHsl(r, g, b);
        
        document.getElementById('hue-slider').value = Math.round(hsl.h);
        
        let adjustedSaturation = hsl.s;
        if (hsl.l > 50) {
            adjustedSaturation = (100 - hsl.l) * 2;
        }
        
        document.getElementById('saturation-slider').value = Math.round(adjustedSaturation);
        document.getElementById('saturation-value').textContent = Math.round(adjustedSaturation);
        
        this.updateSaturationGradient(hsl.h);
    },

    updateRgbFromSliders() {
        if (currentLedType !== 'RGB' && currentLedType !== 'RGBW') return;

        const hue = parseInt(document.getElementById('hue-slider').value);
        const saturation = parseInt(document.getElementById('saturation-slider').value);
        const lightness = 100 - (saturation / 2);
        
        const rgb = ColorUtils.hslToRgb(hue, saturation, lightness);

        const inputs = document.querySelectorAll('#color-inputs-container input[type="number"]');
        if (inputs.length >= 3) {
            inputs[0].value = rgb.r;
            inputs[1].value = rgb.g;
            inputs[2].value = rgb.b;
        }
        
        ColorPreview.update();
    },

    updateRgbwFromSliders() {
        if (currentLedType !== 'RGBW') return;

        this.updateRgbFromSliders();
        
        const whiteValue = parseInt(document.getElementById('white-slider').value);
        const inputs = document.querySelectorAll('#color-inputs-container input[type="number"]');
        if (inputs.length >= 4) {
            inputs[3].value = whiteValue;
        }
        
        ColorPreview.update();
    },

    updateSaturationGradient(hue) {
        const color = ColorUtils.hslToRgb(hue, 100, 50);
        const saturationSlider = document.getElementById('saturation-slider');
        saturationSlider.style.setProperty('--slider-color', `rgb(${color.r}, ${color.g}, ${color.b})`);
        saturationSlider.style.background = `linear-gradient(to right, #ffffff, rgb(${color.r}, ${color.g}, ${color.b}))`;
    },

    updateTempFromWwa() {
        const inputs = document.querySelectorAll('#color-inputs-container input[type="number"]');
        if (inputs.length < 3) return;

        const cw = parseInt(inputs[0].value) || 0;
        const nw = parseInt(inputs[1].value) || 0;
        const ww = parseInt(inputs[2].value) || 0;

        const total = cw + nw + ww;
        if (total === 0) return;

        const warmRatio = (ww + (nw * 0.5)) / total;
        const tempValue = Math.round(warmRatio * 100);
        
        document.getElementById('temp-slider').value = tempValue;
    },

    updateWwaFromTemp() {
        if (currentLedType !== 'WWA') return;

        const tempValue = parseInt(document.getElementById('temp-slider').value);
        const inputs = document.querySelectorAll('#color-inputs-container input[type="number"]');
        if (inputs.length < 3) return;

        const currentCw = parseInt(inputs[0].value) || 0;
        const currentNw = parseInt(inputs[1].value) || 0;
        const currentWw = parseInt(inputs[2].value) || 0;
        const totalBrightness = currentCw + currentNw + currentWw || 255;

        let cw, nw, ww;
        
        if (tempValue <= 50) {
            const ratio = tempValue / 50;
            cw = Math.round(totalBrightness * (1 - ratio));
            nw = Math.round(totalBrightness * ratio);
            ww = 0;
        } else {
            const ratio = (tempValue - 50) / 50;
            cw = 0;
            nw = Math.round(totalBrightness * (1 - ratio));
            ww = Math.round(totalBrightness * ratio);
        }

        // Ensure values don't exceed 255
        cw = Math.min(255, cw);
        nw = Math.min(255, nw);
        ww = Math.min(255, ww);

        inputs[0].value = cw;
        inputs[1].value = nw;
        inputs[2].value = ww;
        
        ColorPreview.update();
    }
};

const ColorPreview = {
    update() {
        const inputs = document.querySelectorAll('#color-inputs-container input[type="number"]');
        const preview = document.getElementById('color-preview');
        
        if (currentLedType === 'RGB' && inputs.length >= 3) {
            const r = parseInt(inputs[0].value) || 0;
            const g = parseInt(inputs[1].value) || 0;
            const b = parseInt(inputs[2].value) || 0;
            preview.style.backgroundColor = `rgb(${r}, ${g}, ${b})`;
        } else if (currentLedType === 'RGBW' && inputs.length >= 4) {
            const r = parseInt(inputs[0].value) || 0;
            const g = parseInt(inputs[1].value) || 0;
            const b = parseInt(inputs[2].value) || 0;
            const w = parseInt(inputs[3].value) || 0;
            
            const mixedR = Math.min(255, r + (w * 0.3));
            const mixedG = Math.min(255, g + (w * 0.3));
            const mixedB = Math.min(255, b + (w * 0.3));
            
            preview.style.backgroundColor = `rgb(${mixedR}, ${mixedG}, ${mixedB})`;
        } else if (currentLedType === 'WWA' && inputs.length >= 3) {
            const cw = parseInt(inputs[0].value) || 0;
            const nw = parseInt(inputs[1].value) || 0;
            const ww = parseInt(inputs[2].value) || 0;
            
            const r = Math.min(255, (cw * 0.7) + (nw * 0.9) + (ww * 1.0));
            const g = Math.min(255, (cw * 0.8) + (nw * 0.9) + (ww * 0.8));
            const b = Math.min(255, (cw * 1.0) + (nw * 0.9) + (ww * 0.3));
            
            preview.style.backgroundColor = `rgb(${r}, ${g}, ${b})`;
        }
    }
};

const ColorUtils = {
    hslToRgb(h, s, l) {
        h = h / 360;
        s = s / 100;
        l = l / 100;

        let r, g, b;

        if (s === 0) {
            r = g = b = l;
        } else {
            const hue2rgb = (p, q, t) => {
                if (t < 0) t += 1;
                if (t > 1) t -= 1;
                if (t < 1/6) return p + (q - p) * 6 * t;
                if (t < 1/2) return q;
                if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
                return p;
            };

            const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
            const p = 2 * l - q;
            r = hue2rgb(p, q, h + 1/3);
            g = hue2rgb(p, q, h);
            b = hue2rgb(p, q, h - 1/3);
        }

        return {
            r: Math.round(r * 255),
            g: Math.round(g * 255),
            b: Math.round(b * 255)
        };
    },

    rgbToHsl(r, g, b) {
        r /= 255;
        g /= 255;
        b /= 255;

        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);
        let h, s, l = (max + min) / 2;

        if (max === min) {
            h = s = 0;
        } else {
            const d = max - min;
            s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

            switch (max) {
                case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
                case g: h = ((b - r) / d + 2) / 6; break;
                case b: h = ((r - g) / d + 4) / 6; break;
            }
        }

        return {
            h: h * 360,
            s: s * 100,
            l: l * 100
        };
    }
};

// ==========================================
// STATIC IP MANAGEMENT
// ==========================================
const StaticIP = {
    updateFields() {
        const staticIpEnabled = document.getElementById('static-ip').checked;
        const staticIpFields = document.querySelectorAll('.static-ip-field');
        
        staticIpFields.forEach(field => {
            field.disabled = !staticIpEnabled;
            field.style.opacity = staticIpEnabled ? '1' : '0.5';
            field.style.backgroundColor = staticIpEnabled ? 'rgba(255, 255, 255, 0.1)' : 'rgba(255, 255, 255, 0.05)';
        });
    }
};

// ==========================================
// UI UTILITIES
// ==========================================
const UI = {
    showSaveButtonState(state, duration = 1000) {
        const saveButton = document.querySelector('.save-btn');
        const colors = {
            success: '#4CAF50',
            error: '#f44336',
            default: ''
        };

        saveButton.style.backgroundColor = colors[state] || colors.default;
        
        setTimeout(() => {
            saveButton.style.backgroundColor = colors.default;
        }, duration);
    }
};

// ==========================================
// DEVICE MANAGEMENT
// ==========================================
const Device = {
    isRestarting: false,
    
    async restart() {
        if (this.isRestarting) {
            return; // Prevent multiple calls
        }
        
        if (!confirm('Are you sure you want to restart the device?')) {
            return;
        }

        this.isRestarting = true;
        const restartBtn = document.getElementById('restart-btn');
        restartBtn.disabled = true;
        restartBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

        try {
            const response = await fetch('/restart', {
                method: 'GET',
                signal: AbortSignal.timeout(3000) // 3 second timeout
            });
            
            // Show notification that device is restarting
            alert('Device is restarting. The page will reload in 15 seconds...');
            
            // Reload page after delay to give device time to restart
            setTimeout(() => {
                window.location.reload();
            }, 15000);
        } catch (error) {
            console.error('Error restarting device:', error);
            // If fetch fails, device might already be restarting
            alert('Restart command sent. The page will reload in 15 seconds...');
            
            setTimeout(() => {
                window.location.reload();
            }, 15000);
        }
    }
};

// ==========================================
// SCROLL PREVENTION FOR SLIDERS
// ==========================================
function preventScrollOnSliders() {
    const sliders = document.querySelectorAll('input[type="range"]');
    
    sliders.forEach(slider => {
        // Only prevent mouse wheel scrolling on sliders (desktop)
        slider.addEventListener('wheel', function(e) {
            e.preventDefault();
        }, { passive: false });
    });
}

// ==========================================
// EVENT LISTENERS
// ==========================================
function attachEventListeners() {
    // Brightness slider
    const brightnessSlider = document.getElementById('brightness-slider');
    const brightnessValue = document.getElementById('brightness-value');
    brightnessSlider.addEventListener('input', function() {
        brightnessValue.textContent = this.value;
    });

    // Hue slider
    const hueSlider = document.getElementById('hue-slider');
    hueSlider.addEventListener('input', function() {
        ColorSliders.updateSaturationGradient(this.value);
        if (currentLedType === 'RGBW') {
            ColorSliders.updateRgbwFromSliders();
        } else {
            ColorSliders.updateRgbFromSliders();
        }
    });

    // Saturation slider
    const saturationSlider = document.getElementById('saturation-slider');
    const saturationValue = document.getElementById('saturation-value');
    saturationSlider.addEventListener('input', function() {
        saturationValue.textContent = this.value;
        if (currentLedType === 'RGBW') {
            ColorSliders.updateRgbwFromSliders();
        } else {
            ColorSliders.updateRgbFromSliders();
        }
    });

    // White slider
    const whiteSlider = document.getElementById('white-slider');
    const whiteValue = document.getElementById('white-value');
    whiteSlider.addEventListener('input', function() {
        whiteValue.textContent = this.value;
        ColorSliders.updateRgbwFromSliders();
    });

    // Temperature slider
    const tempSlider = document.getElementById('temp-slider');
    tempSlider.addEventListener('input', function() {
        if (currentLedType === 'WWA') {
            ColorSliders.updateWwaFromTemp();
        }
    });

    // Static IP checkbox
    document.getElementById('static-ip').addEventListener('change', StaticIP.updateFields);

    // Restart button
    document.getElementById('restart-btn').addEventListener('click', function() {
        Device.restart();
    });

    // Save button
    document.querySelector('.save-btn').addEventListener('click', async function() {
        const saveButton = this;
        saveButton.disabled = true;

        const buttonTimeout = setTimeout(() => {
            saveButton.disabled = false;
        }, 2000);

        try {
            const success = await Config.save();
            clearTimeout(buttonTimeout);
            
            if (success) {
                UI.showSaveButtonState('success');
            }
        } catch (error) {
            clearTimeout(buttonTimeout);
            UI.showSaveButtonState('error');
            alert('Error saving settings. Please try again.');
        } finally {
            saveButton.disabled = false;
        }
    });

    // Input validation for number fields
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('input', function() {
            const min = parseInt(this.min);
            const max = parseInt(this.max);

            if (this.value === '') {
                this.value = 0;
            } else if (parseInt(this.value) < min) {
                this.value = min;
            } else if (parseInt(this.value) > max) {
                this.value = max;
            }
        });
    });
}

// ==========================================
// INITIALIZATION
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
    Config.fetch();
    attachEventListeners();
    preventScrollOnSliders();
});

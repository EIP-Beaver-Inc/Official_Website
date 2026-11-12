
export const PLANK_IMAGE = '/assets/plank-scan.jpg';
export const PLANK_SIZE = { w: 3210, h: 365 };
export const PLANK_RATIO = PLANK_SIZE.w / PLANK_SIZE.h;

export const DEFECT_TYPES = {
    vif: { label: 'Nœud vif', color: 'hsl(120 35% 38%)' },
    mort: { label: 'Nœud mort', color: 'hsl(35 70% 42%)' },
    fissure: { label: 'Fissure', color: 'hsl(var(--primary))' },
};

export const PLANK_DEFECTS = [
    { type: 'fissure', x: 0, y: 56.5, w: 1.1, h: 3.3 },
    { type: 'fissure', x: 0.1, y: 43.8, w: 2.3, h: 5.6 },
    { type: 'fissure', x: 0.2, y: 35.3, w: 3.2, h: 7.1 },
    { type: 'vif', x: 6.1, y: 25.4, w: 2.7, h: 23 },
    { type: 'fissure', x: 6.3, y: 13.2, w: 3.4, h: 8.6 },
    { type: 'vif', x: 26.5, y: 22.2, w: 0.9, h: 8.9 },
    { type: 'vif', x: 29.7, y: 95.9, w: 1.6, h: 4.1 },
    { type: 'vif', x: 34.5, y: 39.9, w: 1, h: 5.6 },
    { type: 'vif', x: 36.4, y: 32, w: 0.6, h: 5.2 },
    { type: 'vif', x: 36.9, y: 11.6, w: 1.1, h: 5.7 },
    { type: 'vif', x: 37, y: 51.6, w: 1.2, h: 12.6 },
    { type: 'vif', x: 37.6, y: 25.5, w: 1.4, h: 5.5 },
    { type: 'vif', x: 55.7, y: 79.5, w: 1.3, h: 10.8 },
    { type: 'vif', x: 59.3, y: 13.1, w: 1, h: 7.3 },
    { type: 'vif', x: 59.3, y: 25.8, w: 0.7, h: 6.7 },
    { type: 'vif', x: 61.2, y: 21.7, w: 1.1, h: 8.2 },
    { type: 'vif', x: 65.7, y: 65.5, w: 1.1, h: 13.1 },
    { type: 'vif', x: 66.1, y: 21.5, w: 0.7, h: 7.3 },
    { type: 'fissure', x: 73.1, y: 85.3, w: 6, h: 2.8 },
    { type: 'vif', x: 78.9, y: 83.1, w: 3.4, h: 16.7 },
    { type: 'fissure', x: 90.9, y: 48.6, w: 5, h: 5.2 },
    { type: 'mort', x: 91.9, y: 23.1, w: 1.2, h: 6.9 },
    { type: 'vif', x: 96, y: 38.7, w: 3.1, h: 20.2 },
];

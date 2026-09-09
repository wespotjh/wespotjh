/* ==========================================================================
   젠제네틱스 홈 — 히어로 (three.js 스크롤 스크럽)

   home-blocks.js 가 먼저 로드되어 window.ZG_HOME 을 만들어 둔다.
   이 파일은 그 위에 얹힌다. 블록은 히어로 없이도 단독으로 동작한다.

   지키는 규칙 (home-blocks.js 와 동일)
     - document.body 에 클래스를 붙이지 않는다. 3D 폴백 상태도 .zg-home 에 붙인다.
       프로토타입은 body.no3d / body.reduced 를 썼는데, 메인 인라인 스크립트가
       body 의 class 속성을 통째로 지우는 경로가 있어 폴백이 조용히 죽는다.
     - window.onload 를 쓰지 않는다
     - 이미지 URL 은 index.html 매니페스트에서만 읽는다 (이 파일에 경로 0개)
     - 배경 사진 5장 중 첫 장은 index.html 이 인라인으로 칠한다.
       나머지 4장은 첫 스크롤 또는 1.5초 뒤에 주입한다 — 첫 화면 전송량을 줄인다.
     - three.js 는 async 로 온다. 부팅 시점에 없으면 일단 폴백(.zg-no3d)으로 그리고,
       도착하면 사용자가 아직 첫 화면 근처일 때만 3D 로 승격한다.
       이미 아래로 내려간 뒤에 승격하면 히어로 높이가 바뀌어 화면이 튄다 — 그때는 폴백을 유지한다.
     - 진행률은 캐시하지 않는다. 스킨이 스크롤 중 문서 높이를 바꾸는 구간이 있다.
   ========================================================================== */
(function () {
  "use strict";

  var ZG = window.ZG_HOME = window.ZG_HOME || {};
  var IMG = window.ZG_HOME_IMG || null;
  if (!ZG.onThaw) ZG.onThaw = function () {};
  if (typeof ZG.frozen !== 'boolean') ZG.frozen = false;

  var BG_CLASS = ['.zg-bg0', '.zg-bgm', '.zg-bg2', '.zg-bg3', '.zg-bg4'];
  var root = null;
  var painted = false;

  /* 배경 4장 지연 주입. .zg-bg0 은 index.html 인라인 style 이 이미 칠했다. */
  function paintRest() {
    if (painted || !root || !IMG || !IMG.bg) return;
    painted = true;
    for (var i = 1; i < BG_CLASS.length && i < IMG.bg.length; i++) {
      var el = root.querySelector(BG_CLASS[i]);
      if (el && !el.style.backgroundImage) {
        el.style.backgroundImage = 'url(' + IMG.base + IMG.bg[i] + ')';
      }
    }
  }

  /* ------------------------------------------------- 하단 고정 바 (3D 무관) */
  function initBar() {
    var bar = root.querySelector('.zg-ctabar');
    if (!bar) return;
    function barCheck() {
      bar.classList.toggle('zg-on', window.pageYOffset > window.innerHeight * 0.6);
    }
    window.addEventListener('scroll', barCheck, { passive: true });
    barCheck();
  }

  /* 히어로 안의 앵커 두 개는 스토어 섹션으로 부드럽게 내린다. */
  function initJump() {
    var list = root.querySelectorAll('[data-zg-jump]');
    var store = root.querySelector('.zg-store');
    if (!store) return;
    for (var i = 0; i < list.length; i++) {
      list[i].addEventListener('click', function (e) {
        e.preventDefault();
        store.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    }
  }

  /* ------------------------------------------------------------- 히어로 3D */
  function initHero() {

  var reduced = root.classList.contains('zg-reduced');
  if (typeof THREE === 'undefined') { root.classList.add('zg-no3d'); return; }

  var canvas = root.querySelector('.zg-scene');
  if (!canvas) return;
  var renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
  } catch (e) { root.classList.add('zg-no3d'); return; }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setClearColor(0x000000, 0);

  var scene = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(42, 1, 0.1, 80);
  camera.position.set(0, 0.7, 9.4);
  camera.lookAt(0, -0.4, 0);

  var amb = new THREE.AmbientLight(0xffffff, 0.75); scene.add(amb);
  var key = new THREE.DirectionalLight(0xffffff, 0.8); key.position.set(4, 7, 6); scene.add(key);
  var warm = new THREE.PointLight(0xB98D5F, 0.6, 18); warm.position.set(-3, -1, 4); scene.add(warm);

  /* ---- color worlds: dawn navy -> magenta morning -> orange dusk -> purple night -> navy finale ---- */
  var W = [
    [0.000, [11, 22, 51], [34, 48, 102], [255, 201, 138]],
    [0.075, [11, 22, 51], [34, 48, 102], [255, 201, 138]],
    [0.159, [61, 10, 38], [190, 28, 84], [255, 109, 155]],
    [0.313, [61, 10, 38], [190, 28, 84], [255, 109, 155]],
    [0.407, [64, 22, 8], [239, 104, 22], [255, 157, 77]],
    [0.547, [64, 22, 8], [239, 104, 22], [255, 157, 77]],
    [0.641, [17, 9, 42], [88, 40, 168], [150, 130, 255]],
    [0.783, [17, 9, 42], [88, 40, 168], [150, 130, 255]],
    [0.894, [11, 22, 51], [22, 41, 92], [126, 141, 180]],
    [1.000, [11, 22, 51], [22, 41, 92], [126, 141, 180]]
  ];
  function worldAt(p) {
    var a = W[0], b = W[W.length - 1];
    for (var i = 0; i < W.length - 1; i++) {
      if (p >= W[i][0] && p <= W[i + 1][0]) { a = W[i]; b = W[i + 1]; break; }
    }
    var t0 = (p - a[0]) / (b[0] - a[0] || 1);
    var t = t0 * t0 * (3 - 2 * t0);
    function mix(c1, c2) {
      return [c1[0] + (c2[0] - c1[0]) * t, c1[1] + (c2[1] - c1[1]) * t, c1[2] + (c2[2] - c1[2]) * t];
    }
    return [mix(a[1], b[1]), mix(a[2], b[2]), mix(a[3], b[3])];
  }
  function rgbStr(c) { return 'rgb(' + Math.round(c[0]) + ',' + Math.round(c[1]) + ',' + Math.round(c[2]) + ')'; }

  /* ---- glow orb behind the pouch (the reference's centered sun) ---- */
  function orbTexture() {
    var c = document.createElement('canvas'); c.width = 256; c.height = 256;
    var g = c.getContext('2d');
    var grad = g.createRadialGradient(128, 128, 10, 128, 128, 128);
    grad.addColorStop(0, 'rgba(255,255,255,1)');
    grad.addColorStop(0.28, 'rgba(255,255,255,0.55)');
    grad.addColorStop(0.6, 'rgba(255,255,255,0.16)');
    grad.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = grad; g.fillRect(0, 0, 256, 256);
    return new THREE.CanvasTexture(c);
  }
  /* a proper sun: crisp disc + soft halo */
  function sunTexture() {
    var c = document.createElement('canvas'); c.width = 256; c.height = 256;
    var g = c.getContext('2d');
    var grad = g.createRadialGradient(128, 128, 8, 128, 128, 128);
    grad.addColorStop(0, 'rgba(255,255,255,1)');
    grad.addColorStop(0.2, 'rgba(255,255,255,0.98)');
    grad.addColorStop(0.26, 'rgba(255,255,255,0.4)');
    grad.addColorStop(0.55, 'rgba(255,255,255,0.13)');
    grad.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = grad; g.fillRect(0, 0, 256, 256);
    return new THREE.CanvasTexture(c);
  }
  /* a crescent moon with a soft glow */
  function moonTexture() {
    var c = document.createElement('canvas'); c.width = 256; c.height = 256;
    var g = c.getContext('2d');
    var halo = g.createRadialGradient(128, 128, 20, 128, 128, 128);
    halo.addColorStop(0, 'rgba(255,255,255,0.35)');
    halo.addColorStop(0.5, 'rgba(255,255,255,0.1)');
    halo.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = halo; g.fillRect(0, 0, 256, 256);
    g.fillStyle = 'rgba(255,255,255,0.98)';
    g.beginPath(); g.arc(128, 128, 52, 0, 6.283); g.fill();
    g.globalCompositeOperation = 'destination-out';
    g.beginPath(); g.arc(158, 108, 48, 0, 6.283); g.fill();
    g.globalCompositeOperation = 'source-over';
    return new THREE.CanvasTexture(c);
  }

  /* the sun & moon live in the DOM, not WebGL — iOS는 저알파 WebGL 그라데이션을
     무지개 노이즈로 깨뜨리므로 CSS 그라데이션/2D 캔버스로 그리고 3D 좌표만 투영한다 */
  var sunDom = root.querySelector('.zg-sun'), moonDom = root.querySelector('.zg-moon');
  if (!sunDom || !moonDom) { root.classList.add('zg-no3d'); return; }
  (function () {
    var g = moonDom.getContext('2d');
    var halo = g.createRadialGradient(128, 128, 20, 128, 128, 128);
    halo.addColorStop(0, 'rgba(237,232,255,0.35)');
    halo.addColorStop(0.5, 'rgba(237,232,255,0.1)');
    halo.addColorStop(1, 'rgba(237,232,255,0)');
    g.fillStyle = halo; g.fillRect(0, 0, 256, 256);
    g.fillStyle = 'rgba(240,237,255,0.98)';
    g.beginPath(); g.arc(128, 128, 52, 0, 6.283); g.fill();
    g.globalCompositeOperation = 'destination-out';
    g.beginPath(); g.arc(158, 108, 48, 0, 6.283); g.fill();
    g.globalCompositeOperation = 'source-over';
  })();
  var sun = { position: new THREE.Vector3(-2.5, -0.5, -9) };
  var moon = { position: new THREE.Vector3(2.4, -2.6, -9) };
  var lastSunGrad = '';
  function sunGradient(r, gg, b) {
    var c = Math.round(r * 255) + ',' + Math.round(gg * 255) + ',' + Math.round(b * 255);
    var s = 'radial-gradient(circle, #fff 0%, #fff 10%, rgba(' + c + ',0.4) 13%, rgba(' + c + ',0.13) 27%, rgba(' + c + ',0) 50%)';
    if (s !== lastSunGrad) { lastSunGrad = s; sunDom.style.background = s; }
  }
  var skyV = new THREE.Vector3();
  function placeSky(el, pos, worldSize, op) {
    skyV.copy(pos).project(camera);
    var sw = renderer.domElement.clientWidth, sh = renderer.domElement.clientHeight;
    var fovPx = sh / (2 * Math.tan(camera.fov * Math.PI / 360));
    var px = worldSize / camera.position.distanceTo(pos) * fovPx;
    el.style.opacity = op.toFixed(3);
    el.style.width = px.toFixed(1) + 'px'; el.style.height = px.toFixed(1) + 'px';
    el.style.transform = 'translate(' + ((skyV.x + 1) / 2 * sw - px / 2).toFixed(1) + 'px,' +
      ((1 - skyV.y) / 2 * sh - px / 2).toFixed(1) + 'px)';
  }

  var orbLight = new THREE.PointLight(0xFFE9C0, 0.45, 24); orbLight.position.set(0, 2.2, -3.5); scene.add(orbLight);

  /* shooting stars for the night world */
  function meteorTexture() {
    var c = document.createElement('canvas'); c.width = 128; c.height = 8;
    var g = c.getContext('2d');
    var grad = g.createLinearGradient(0, 0, 128, 0);
    grad.addColorStop(0, 'rgba(255,255,255,0)');
    grad.addColorStop(0.75, 'rgba(255,255,255,0.55)');
    grad.addColorStop(0.96, 'rgba(255,255,255,1)');
    grad.addColorStop(1, 'rgba(255,255,255,1)');
    g.fillStyle = grad; g.fillRect(0, 0, 128, 8);
    return new THREE.CanvasTexture(c);
  }
  var meteorTex = meteorTexture();
  var meteors = [];
  for (var mi = 0; mi < 3; mi++) {
    var mMat = new THREE.MeshBasicMaterial({ map: meteorTex, transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide });
    var mm2 = new THREE.Mesh(new THREE.PlaneGeometry(1.7, 0.035), mMat);
    mm2.rotation.z = -0.55;
    mm2.position.z = -8;
    mm2.userData = { x0: -2.2 + mi * 2.4, y0: 3.6 - mi * 0.4, dur: 0.85, cyc: 4.6 + mi * 2.3, off: mi * 1.9 };
    scene.add(mm2); meteors.push(mm2);
  }

  /* ---- stars ---- */
  var starN = 260;
  var starGeo = new THREE.BufferGeometry();
  var starPos = new Float32Array(starN * 3);
  for (var si = 0; si < starN; si++) {
    starPos[si * 3] = (Math.random() - 0.5) * 34;
    starPos[si * 3 + 1] = Math.random() * 14 + 0.5;
    starPos[si * 3 + 2] = -8 - Math.random() * 10;
  }
  starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
  var starMat = new THREE.PointsMaterial({ color: 0xFFFFFF, size: 0.07, transparent: true, opacity: 0, depthWrite: false });
  scene.add(new THREE.Points(starGeo, starMat));

  /* ---- REAL render textures: 앞/뒷면 세로 크롭 — 순서 [비타민B, 칼륨, 마그네슘] = 비트 M/E/N ---- */
  var RF = (IMG && IMG.tex ? IMG.tex : []).map(function (n) { return IMG.base + n; });
  if (RF.length < 3) { root.classList.add('zg-no3d'); return; }
  var texLoader = new THREE.TextureLoader();
  var fronts = RF.map(function (src) { var t = texLoader.load(src); t.anisotropy = 4; return t; });

  /* ---- the one pouch: 실제 렌더 앞/뒷면을 통통한 파우치 지오메트리에 입혀
     세워진 채 '세로축'으로 돈다. 단면은 렌더 측면 실측(두께 ≈ 폭의 27%)의 렌즈형 ---- */
  var STICK_H = 3.2, STICK_W = STICK_H * (155 / 700), STICK_T = STICK_W * 0.27;
  function pouchSheet() {
    var g = new THREE.PlaneGeometry(STICK_W, STICK_H, 20, 44);
    var pa = g.attributes.position;
    for (var vi = 0; vi < pa.count; vi++) {
      var vu = pa.getX(vi) / (STICK_W / 2), vv = pa.getY(vi) / (STICK_H / 2);
      var lens = Math.sqrt(Math.max(0, 1 - vu * vu * vu * vu));   /* 가운데가 통통한 단면 */
      var av = Math.abs(vv);
      var taper = av > 0.8 ? Math.max(0, (1 - av) / 0.2) : 1;    /* 위아래 씰은 납작하게 */
      pa.setZ(vi, STICK_T * 0.5 * lens * Math.sqrt(taper));
    }
    g.computeVertexNormals();
    return g;
  }
  var sheetGeo = pouchSheet();
  var bodyLabel = new THREE.MeshBasicMaterial({ map: fronts[0], transparent: true, opacity: 1 });
  var backMat = new THREE.MeshBasicMaterial({ map: fronts[0], transparent: true, opacity: 1 });
  var pouch = new THREE.Group();
  var bodyF = new THREE.Mesh(sheetGeo, bodyLabel);
  var bodyB = new THREE.Mesh(sheetGeo, backMat);
  bodyB.rotation.y = Math.PI;
  bodyF.position.y = bodyB.position.y = 1.35;
  pouch.add(bodyF); pouch.add(bodyB);
  pouch.position.set(0, -2.45, 0.4);
  scene.add(pouch);
  var sideMat = { opacity: 1 };   /* kept for shared fade code */

  /* ---- contact shadow: grounds the pouch on the table ---- */
  function shadowTexture() {
    var c = document.createElement('canvas'); c.width = 256; c.height = 128;
    var g = c.getContext('2d');
    var grad = g.createRadialGradient(128, 64, 6, 128, 64, 64);
    grad.addColorStop(0, 'rgba(10,8,20,0.75)');
    grad.addColorStop(0.55, 'rgba(10,8,20,0.32)');
    grad.addColorStop(1, 'rgba(10,8,20,0)');
    g.save(); g.translate(0, 32); g.scale(1, 0.5);
    g.fillStyle = grad; g.fillRect(0, 0, 256, 256); g.restore();
    return new THREE.CanvasTexture(c);
  }
  var shadowMat = new THREE.MeshBasicMaterial({ map: shadowTexture(), transparent: true, depthWrite: false, opacity: 0.85 });
  var shadow = new THREE.Mesh(new THREE.PlaneGeometry(3.4, 1.7), shadowMat);
  shadow.rotation.x = -Math.PI / 2;
  shadow.position.set(0, -2.42, 0.45);
  scene.add(shadow);

  /* ---- ambient glow dust: tiny drifting sparkles in the world's color ---- */
  var dustN = 260;
  var dustGeo = new THREE.BufferGeometry();
  var dustPos = new Float32Array(dustN * 3);
  for (var di2 = 0; di2 < dustN; di2++) {
    dustPos[di2 * 3] = (Math.random() - 0.5) * 13;
    dustPos[di2 * 3 + 1] = -2.4 + Math.random() * 6.5;
    dustPos[di2 * 3 + 2] = -4.5 + Math.random() * 6;
  }
  dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPos, 3));
  function dotTexture() {
    var c = document.createElement('canvas'); c.width = 32; c.height = 32;
    var g = c.getContext('2d');
    var grad = g.createRadialGradient(16, 16, 1, 16, 16, 15);
    grad.addColorStop(0, 'rgba(255,255,255,1)');
    grad.addColorStop(0.4, 'rgba(255,255,255,0.7)');
    grad.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = grad; g.fillRect(0, 0, 32, 32);
    return new THREE.CanvasTexture(c);
  }
  var dustMat = new THREE.PointsMaterial({ color: 0xFFE2C0, size: 0.07, map: dotTexture(), transparent: true, opacity: 0.4, depthWrite: false, blending: THREE.AdditiveBlending });
  var dust = new THREE.Points(dustGeo, dustMat);
  scene.add(dust);

  /* ---- light streaks sweeping behind the product (dusk energy) ---- */
  var streaks = [];
  for (var sk = 0; sk < 4; sk++) {
    var skMat = new THREE.MeshBasicMaterial({ color: 0xFFD9A8, transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide });
    var skm = new THREE.Mesh(new THREE.PlaneGeometry(8 + sk * 2, 0.05 + sk * 0.02), skMat);
    skm.rotation.z = -0.16 - sk * 0.03;
    skm.position.set(0, 0.4 + sk * 0.85 - (sk === 3 ? 3.1 : 0), -3.5 - sk * 0.7);
    skm.userData = { sp: 1.6 + sk * 0.7, off: sk * 5.2 };
    scene.add(skm); streaks.push(skm);
  }

  /* ---- neon deco props: rings, spheres, diamonds in each world's accent ---- */
  var propCols = [0xFF8FA3, 0xFFB566, 0xB9A5F0];
  var propSets = [];
  var propLayouts = [
    [[-2.6, 1.3, -2.2], [2.4, 2.1, -3.2], [2.0, -1.1, -1.2]],
    [[2.6, 1.7, -2.6], [-2.3, 2.4, -3.2], [-2.1, -0.9, -1.1]],
    [[-2.4, 2.1, -3.0], [2.5, 1.1, -2.2], [-2.0, -1.2, -1.4]]
  ];
  for (var ps = 0; ps < 3; ps++) {
    var set = [];
    var geos = [
      new THREE.TorusGeometry(0.42, 0.045, 12, 40),
      new THREE.SphereGeometry(0.17, 20, 20),
      new THREE.OctahedronGeometry(0.24)
    ];
    for (var pg = 0; pg < 3; pg++) {
      var pm = new THREE.Mesh(geos[pg], new THREE.MeshBasicMaterial({ color: propCols[ps], transparent: true, opacity: 0 }));
      var L = propLayouts[ps][pg];
      pm.userData = { bx: L[0], by: L[1], bz: L[2], ph: ps * 2.1 + pg * 1.3 };
      pm.position.set(L[0], L[1], L[2]);
      scene.add(pm); set.push(pm);
    }
    propSets.push(set);
  }

  /* ---- finale satellites: the other two pouches join, tilted (all three, all day) ---- */
  function makeMini(labelIdx, tilt) {
    var fm = new THREE.MeshBasicMaterial({ map: fronts[labelIdx], transparent: true, opacity: 0 });
    var bm = new THREE.MeshBasicMaterial({ map: fronts[labelIdx], transparent: true, opacity: 0 });
    var grp = new THREE.Group();
    var fMesh = new THREE.Mesh(sheetGeo, fm);
    var bMesh = new THREE.Mesh(sheetGeo, bm);
    bMesh.rotation.y = Math.PI;
    grp.add(fMesh); grp.add(bMesh);
    grp.scale.set(0.62, 0.62, 0.62);
    grp.rotation.z = tilt;
    grp.userData.mats = [fm, bm];
    scene.add(grp);
    return grp;
  }
  var miniA = makeMini(0, 0.26);   /* vitamin B, tilted right */
  var miniB = makeMini(1, -0.26);  /* potassium, tilted left */

  /* ---- powder particles: pour per beat, rest on table, then split ---- */
  var narrowGuess = window.innerWidth / window.innerHeight < 0.85;
  var N = narrowGuess ? 900 : 1400;
  var geo = new THREE.BufferGeometry();
  var pos = new Float32Array(N * 3);
  var col = new Float32Array(N * 3);
  var meta = [];
  /* stream order on screen: 칼륨(blue) / 마그네슘(sand) / 비타민B(gold) */
  var streamCols = [[1.0, 0.63, 0.38], [0.75, 0.66, 0.94], [1.0, 0.58, 0.66]];
  var beatOfSt = { 0: 1, 1: 2, 2: 0 };   /* blue->evening, sand->night, gold->morning */
  var streamX = narrowGuess ? [-1.55, 0, 1.55] : [-2.7, 0, 2.7];
  for (var i = 0; i < N; i++) {
    var st = i % 3;
    meta.push({ d: Math.random() * 0.5, s: 0.7 + Math.random() * 0.6, jx: (Math.random() - 0.5), jz: (Math.random() - 0.5) * 0.5, st: st, ph: Math.random() });
    pos[i * 3 + 1] = -50;
    var sc0 = streamCols[st];
    col[i * 3] = sc0[0]; col[i * 3 + 1] = sc0[1]; col[i * 3 + 2] = sc0[2];
  }
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  var pmat = new THREE.PointsMaterial({ size: 0.06, map: dotTexture(), vertexColors: true, transparent: true, opacity: 0.95, depthWrite: false });
  scene.add(new THREE.Points(geo, pmat));

  /* ---- helpers ---- */
  function clamp01(v) { return v < 0 ? 0 : (v > 1 ? 1 : v); }
  function smooth(a, b, v) { var t = clamp01((v - a) / (b - a)); return t * t * (3 - 2 * t); }
  function lerp(a, b, t) { return a + (b - a) * t; }

  /* beats: morning(vitB) / evening(potassium) / night(magnesium) — 오후 3시 구간 제거(2026-09-07) */
  var beats = [ { s: 0.100, e: 0.313 }, { s: 0.360, e: 0.547 }, { s: 0.594, e: 0.783 } ];
  var FIN0 = 0.830, FIN1 = 0.968;

  var track = root.querySelector('.zg-hero-track');
  var capA = root.querySelector('.zg-cap-a'), capM = root.querySelector('.zg-cap-m'),
      capE = root.querySelector('.zg-cap-e'),
      capN2 = root.querySelector('.zg-cap-n'), capS = root.querySelector('.zg-cap-s');
  var bgEls = BG_CLASS.map(function (c) { return root.querySelector(c); });
  var bgGrade = root.querySelector('.zg-bggrade');
  var hint = root.querySelector('.zg-scroll-hint');
  var bws = [0, 1, 2, 3, 4].map(function (i) { return root.querySelector('.zg-bw' + i); });
  var chipsM = root.querySelectorAll('.zg-co-m .zg-chip');
  var chipsE = root.querySelectorAll('.zg-co-e .zg-chip');
  var chipsN = root.querySelectorAll('.zg-co-n .zg-chip');
  var dashEls = root.querySelectorAll('.zg-dashes span');
  var dashIdx = 0;

  function capFade(el, o) {
    el.style.opacity = o.toFixed(3);
    el.style.transform = 'translateY(' + (24 * (1 - o)).toFixed(1) + 'px)';
  }
  function word(el, o, drift, sc) {
    var s = sc || 1;
    if (skyXF < 1) s = 1 + (s - 1) * 0.3;   /* mobile: soften the zoom so words stay inside the frame */
    el.style.opacity = o.toFixed(3);
    el.style.transform = 'translate(calc(-50% + ' + drift.toFixed(2) + 'vw), -50%) scale(' + s.toFixed(3) + ')';
  }
  function chipFade(list, s, e, p) {
    for (var i = 0; i < list.length; i++) {
      var d = i * 0.025;
      var o = smooth(s + d, s + d + 0.04, p) * (1 - smooth(e - 0.02, e + 0.02, p));
      list[i].style.opacity = o.toFixed(3);
      list[i].style.transform = 'translateY(' + (10 * (1 - o)).toFixed(1) + 'px)';
    }
  }

  var pTarget = 0, pNow = 0, mouseX = 0, skyXF = 1;
  window.addEventListener('mousemove', function (e) { mouseX = (e.clientX / window.innerWidth - 0.5); }, { passive: true });
  /* 히어로가 화면에서 완전히 벗어났는가. 벗어나 있으면 프레임 루프가 three.js 렌더를 건너뛴다 —
     아래 제품 블록의 가루 시퀀스를 훑는 동안에도 WebGL 이 계속 그리면 메인 스레드가 포화된다
     (실측: 모바일 CPU 6배 스로틀 390×844 에서 12.6fps · 프레임 79ms · 롱태스크 5.4초
      → 렌더 정지 후 59.8fps · 16.5ms · 롱태스크 0). */
  var onStage = true;
  function onScroll() {
    var rect = track.getBoundingClientRect();
    onStage = rect.bottom > -80;
    if (reduced || ZG.frozen) { if (reduced) pTarget = 0; return; }
    var total = track.offsetHeight - window.innerHeight;
    pTarget = total > 0 ? clamp01(-rect.top / total) : 0;
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('scroll', paintRest, { passive: true, once: true });
  setTimeout(paintRest, 1500);
  ZG.onThaw(onScroll);

  function resize() {
    var w = canvas.clientWidth || window.innerWidth;
    var h = canvas.clientHeight || window.innerHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    var narrow = w / h < 0.85;
    streamX = narrow ? [-1.55, 0, 1.55] : [-2.7, 0, 2.7];
    skyXF = narrow ? 0.5 : 1;   /* portrait sees a narrow slice of sky — pull the arc in */
  }
  window.addEventListener('resize', resize);
  resize(); onScroll();

  var clock = new THREE.Clock();
  var currentLabel = 0;

  function frame() {
    requestAnimationFrame(frame);
    if (ZG.frozen) return;
    /* 화면 밖에서는 그리지 않는다. 진행률은 목표값에 붙여 둬 되돌아왔을 때 따라잡기 연출이 없다. */
    if (!onStage) { pNow = pTarget; return; }
    var t = clock.getElapsedTime();
    pNow += (pTarget - pNow) * 0.09;
    var p = pNow;

    /* photo crossfade: yoga dawn -> singing bird -> dusk drive -> night sky -> arms-up finale */
    bgEls[0].style.opacity = (1 - smooth(0.075, 0.135, p)).toFixed(3);
    bgEls[1].style.opacity = (smooth(0.075, 0.135, p) * (1 - smooth(0.325, 0.375, p))).toFixed(3);
    bgEls[2].style.opacity = (smooth(0.325, 0.375, p) * (1 - smooth(0.558, 0.629, p))).toFixed(3);
    bgEls[3].style.opacity = (smooth(0.558, 0.629, p) * (1 - smooth(0.830, 0.894, p))).toFixed(3);
    bgEls[4].style.opacity = smooth(0.830, 0.894, p).toFixed(3);

    /* color-world grade painted over the photo — light enough to let the photo breathe */
    var wd = worldAt(p);
    function rgbaStr(c, a) { return 'rgba(' + Math.round(c[0]) + ',' + Math.round(c[1]) + ',' + Math.round(c[2]) + ',' + a + ')'; }
    bgGrade.style.background = 'linear-gradient(180deg,' + rgbaStr(wd[0], 0.52) + ' 0%,' + rgbaStr(wd[1], 0.26) + ' 55%,' + rgbaStr(wd[0], 0.8) + ' 100%)';
    var nightF = smooth(0.570, 0.665, p);

    /* the sun tells the time: dawn left -> overhead -> dusk right */
    var pulse = 1 + Math.sin(t * 1.1) * 0.02;
    var sunP = clamp01(p / 0.570);
    var th = lerp(2.85, 0.25, sunP);
    var setDrop = smooth(0.500, 0.606, p) * 1.6;
    sun.position.set(Math.cos(th) * 5.2 * skyXF, -2.0 + Math.sin(th) * 5.3 - setDrop, -9);
    var sunSize = (6 + (1 - Math.sin(th)) * 3) * pulse;
    sunGradient(
      wd[2][0] / 255 + (1 - wd[2][0] / 255) * 0.45,
      wd[2][1] / 255 + (1 - wd[2][1] / 255) * 0.45,
      wd[2][2] / 255 + (1 - wd[2][2] / 255) * 0.45);
    var sunOp = 0.95 * (1 - smooth(0.570, 0.641, p));

    /* the moon rises with the purple world */
    var moonP = smooth(0.594, 0.736, p);
    moon.position.set(lerp(3.9, 2.4, moonP) * skyXF, lerp(-2.6, 2.7, moonP), -9);
    var moonSize = 3.4 * pulse;
    var moonOp = moonP * (1 - smooth(0.851, 0.926, p) * 0.4);

    /* scene light follows whoever is in the sky */
    orbLight.color.setRGB(wd[2][0] / 255, wd[2][1] / 255, wd[2][2] / 255);
    orbLight.intensity = 0.45 * (1 - nightF) + 0.3 * nightF;
    orbLight.position.x = lerp(sun.position.x, moon.position.x, nightF) * 0.4;

    /* shooting stars streak across the purple night */
    var mAll = nightF * (1 - smooth(0.851, 0.926, p) * 0.6);
    for (var mt = 0; mt < meteors.length; mt++) {
      var me = meteors[mt]; var mu = me.userData;
      var ct = (t + mu.off) % mu.cyc;
      var mp2 = ct / mu.dur;
      if (mp2 < 1 && mAll > 0.02) {
        me.position.x = (mu.x0 + mp2 * 2.6) * skyXF;
        me.position.y = mu.y0 - mp2 * 1.8;
        me.material.opacity = Math.sin(mp2 * Math.PI) * 0.9 * mAll;
      } else {
        me.material.opacity = 0;
      }
    }

    starMat.opacity = nightF * 0.95 * (1 - smooth(0.830, 0.915, p) * 0.7);
    amb.intensity = lerp(0.75, 0.6, nightF);
    key.intensity = lerp(0.8, 0.6, nightF);

    /* which beat is (or was last) active */
    var bIdx = 0, q = 0;
    for (var b = 0; b < 3; b++) {
      if (p >= beats[b].s) { bIdx = b; q = clamp01((p - beats[b].s) / (beats[b].e - beats[b].s)); }
    }
    var started = p >= beats[0].s;

    /* label swap at each beat start (with a quick dip) */
    var wantLabel = started ? bIdx : 0;
    currentLabel = wantLabel;
    var dip = started && q < 0.10 ? 0.35 + q * 6.5 : 1;
    /* the pouch stays hidden through the intro — it enters with MORNING */
    var introF = smooth(0.075, 0.124, p);
    bodyLabel.opacity = Math.min(1, dip) * introF;
    sideMat.opacity = introF;

    /* pouch: stands center stage, turning on its vertical axis with the scroll
       (one full 360° per time of day) — no tearing, ever */
    /* rotation: the original scroll-linked turntable speed — untouched.
       Dynamism comes from FRAMING instead: each scene composes differently. */
    pouch.rotation.y = t * 0.12 + p * Math.PI * 6 + mouseX * 0.3;
    /* 뒷면 디자인은 쓰지 않는다: 카메라 반대편으로 돌아간 면을 현재 제품 '앞면'으로
       몰래 교체 — 반 바퀴 돌 때마다 항상 앞면이 나타나는 캐러셀 */
    var facing = Math.cos(pouch.rotation.y);
    /* 비트가 막 시작했거나(디졸브 중) 로드 직후엔 보이는 면도 강제 동기화 */
    var forceSwap = (started && q < 0.04) || t < 0.6;
    if ((forceSwap || facing < -0.05) && bodyLabel.map !== fronts[currentLabel]) { bodyLabel.map = fronts[currentLabel]; bodyLabel.needsUpdate = true; }
    if ((forceSwap || facing > 0.05) && backMat.map !== fronts[currentLabel]) { backMat.map = fronts[currentLabel]; backMat.needsUpdate = true; }
    var w1 = smooth(0.100, 0.171, p) * (1 - smooth(0.289, 0.360, p));
    var w2 = smooth(0.360, 0.430, p) * (1 - smooth(0.523, 0.594, p));
    var w3 = smooth(0.594, 0.665, p) * (1 - smooth(0.759, 0.841, p));
    pouch.rotation.z = Math.sin(t * 0.6) * 0.015 + 0.09 * w2;   /* evening: diagonal cruise lean */
    pouch.rotation.x = -0.07 * w3;                              /* night: restful lean back */
    /* finale: lift off and shrink a touch so the stream labels stay clear */
    var fin = smooth(0.841, 0.926, p);
    pouch.position.y = -2.45 + fin * 1.45 - (1 - introF) * 0.9 + Math.sin(t * 0.9) * 0.02;
    /* framing: each scene composes differently — morning right of center,
       evening left with the lean, night dead center */
    var offX = skyXF < 1 ? 0.45 : 0.75;
    pouch.position.x = offX * w1 - offX * w2;
    pouch.position.z = 0.4;
    var psc = 1 - fin * 0.2;
    pouch.scale.set(psc, psc, psc);
    backMat.opacity = introF;

    /* ---- dynamics: beat zoom factor + transition energy ---- */
    var zi = started ? Math.sin(Math.PI * q) : 0;   /* peaks mid-beat, 0 between beats */
    var trans = smooth(0.301, 0.348, p) * (1 - smooth(0.372, 0.418, p))
              + smooth(0.523, 0.558, p) * (1 - smooth(0.606, 0.653, p));
    var propXF = skyXF < 1 ? 0.72 : 1;

    /* neon props: each world's set floats in while its beat plays */
    for (var g2 = 0; g2 < 3; g2++) {
      var bt2 = beats[g2];
      var po = smooth(bt2.s + 0.02, bt2.s + 0.08, p) * (1 - smooth(bt2.e - 0.03, bt2.e + 0.02, p));
      var set2 = propSets[g2];
      for (var pe = 0; pe < set2.length; pe++) {
        var prm = set2[pe]; var ud = prm.userData;
        prm.material.opacity = po * 0.92;
        prm.position.x = ud.bx * propXF * (1 + (1 - po) * 0.5);
        prm.position.y = ud.by + Math.sin(t * 0.8 + ud.ph) * 0.18;
        prm.rotation.x = t * 0.5 + ud.ph;
        prm.rotation.y = t * 0.7 + ud.ph;
      }
    }

    /* light streaks: always breathing faintly, surging at dusk and on transitions */
    var evF = smooth(0.360, 0.430, p) * (1 - smooth(0.547, 0.617, p));
    for (var s2 = 0; s2 < streaks.length; s2++) {
      var stk = streaks[s2];
      stk.position.x = ((t * stk.userData.sp + stk.userData.off) % 22) - 11;
      stk.material.opacity = 0.08 + evF * 0.4 + trans * 0.45;
      stk.material.color.setRGB(wd[2][0] / 255, wd[2][1] / 255, wd[2][2] / 255);
    }

    /* glow dust in the world's tint */
    dust.rotation.y = t * 0.02;
    dustMat.color.setRGB(
      wd[2][0] / 255 * 0.55 + 0.45,
      wd[2][1] / 255 * 0.55 + 0.45,
      wd[2][2] / 255 * 0.55 + 0.45);
    dustMat.opacity = 0.3 + trans * 0.25 + zi * 0.12;

    /* contact shadow: leans away from the sun, releases as the pouch lifts */
    shadow.position.x = pouch.position.x - sun.position.x * 0.04;
    var shSc = (1 - fin * 0.4) * (1 - zi * 0.1);
    shadow.scale.set(shSc, shSc, 1);
    shadowMat.opacity = 0.85 * (1 - fin * 0.55) * introF;

    /* finale satellites: the other two pouches tilt in beside the hero */
    var satX = skyXF < 1 ? 1.5 : 2.5;
    miniA.position.set(satX, -1.15 + fin * 0.4 + Math.sin(t * 0.9) * 0.06, -1.2);
    miniB.position.set(-satX, -1.3 + fin * 0.4 + Math.sin(t * 0.9 + 2) * 0.06, -1.2);
    miniA.rotation.y = t * 0.5;
    miniB.rotation.y = -t * 0.45;
    miniA.userData.mats[0].opacity = miniA.userData.mats[1].opacity = fin;
    miniB.userData.mats[0].opacity = miniB.userData.mats[1].opacity = fin;

    /* powder: rises from the bottom, spirals around the turning pouch,
       settles at its base — then joins its stream in the finale */
    var split = smooth(FIN0, FIN1, p);
    var attr = geo.attributes.position.array;
    /* per-time character: morning lively, evening steady, night slow & wide */
    var swirlP = [ { h: 2.6, w: 1.1, r: 1.15 }, { h: 2.1, w: 0.6, r: 0.95 }, { h: 1.6, w: 0.35, r: 1.5 } ];
    for (var i2 = 0; i2 < N; i2++) {
      var md = meta[i2];
      var pbeat = beatOfSt[md.st];
      var bt = beats[pbeat];
      var bq = clamp01((p - bt.s) / (bt.e - bt.s));
      var fp = clamp01((bq - 0.18 - md.d * 0.45) / 0.6);
      var x3, y3, z3;
      if (fp <= 0) { attr[i2 * 3 + 1] = -50; continue; }
      var sw = swirlP[pbeat];
      if (fp < 1) {
        var ang = md.ph * 6.283 + t * sw.w + fp * 2.2;
        var rad = (0.85 + Math.abs(md.jx) * sw.r) * (1 + fp * 0.35);
        x3 = pouch.position.x + Math.cos(ang) * rad;
        z3 = pouch.position.z + Math.sin(ang) * rad * 0.45;
        /* rise from below the table, arc up alongside the pouch, sink back to its base */
        y3 = -2.35 + Math.sin(fp * Math.PI) * sw.h * md.s - (1 - fp) * 0.9;
        if (y3 < -2.9) y3 = -2.9;
      } else {
        /* settles into three soft piles at the base */
        var pileX = pbeat === 0 ? 1.05 : (pbeat === 1 ? 0 : -1.05);
        var pileW = pbeat === 2 ? 1.6 : 1.2;
        x3 = pileX + md.jx * pileW;
        y3 = -2.32 + Math.abs(md.jz) * 0.08 + md.d * 0.05;
        z3 = 0.4 + md.jz * 0.9;
      }
      var flow = (md.ph + t * 0.22) % 1;
      var sx = streamX[md.st] + md.jx * 0.5 + Math.sin(t * 1.4 + md.ph * 9) * 0.07;
      var sy = 1.5 - flow * 4.0;
      var sz = -1.6 + md.jz * 0.8;   /* streams flow behind the pouch */
      attr[i2 * 3] = lerp(x3, sx, split);
      attr[i2 * 3 + 1] = lerp(y3, sy, split);
      attr[i2 * 3 + 2] = lerp(z3, sz, split);
    }
    geo.attributes.position.needsUpdate = true;

    /* captions */
    capFade(capA, 1 - smooth(0.063, 0.124, p));
    capFade(capM, smooth(0.112, 0.159, p) * (1 - smooth(0.289, 0.348, p)));
    capFade(capE, smooth(0.372, 0.418, p) * (1 - smooth(0.523, 0.570, p)));
    capFade(capN2, smooth(0.606, 0.653, p) * (1 - smooth(0.759, 0.818, p)));
    capFade(capS, smooth(0.862, 0.926, p));
    hint.style.opacity = (1 - smooth(0.025, 0.088, p)).toFixed(2);

    /* giant words: crossfade + slow horizontal drift, one per world */
    var q1 = clamp01((p - 0.100) / 0.213),
        q2 = clamp01((p - 0.360) / 0.187), q3 = clamp01((p - 0.594) / 0.189);
    var driftF = skyXF < 1 ? 4 : 10;   /* smaller drift on mobile so words never leave the frame */
    word(bws[0], 0.12 * (1 - smooth(0.063, 0.124, p)), 0);
    word(bws[1], 0.55 * smooth(0.112, 0.159, p) * (1 - smooth(0.301, 0.360, p)), (0.5 - q1) * driftF, 1.14 - q1 * 0.18);
    word(bws[2], 0.55 * smooth(0.372, 0.418, p) * (1 - smooth(0.523, 0.582, p)), (0.5 - q2) * driftF, 1.14 - q2 * 0.18);
    word(bws[3], 0.50 * smooth(0.606, 0.653, p) * (1 - smooth(0.771, 0.830, p)), (0.5 - q3) * driftF, 1.14 - q3 * 0.18);
    word(bws[4], 0.14 * smooth(0.873, 0.926, p), 0);

    /* spec callout chips, staggered per beat */
    chipFade(chipsM, 0.124, 0.325, p);
    chipFade(chipsE, 0.383, 0.547, p);
    chipFade(chipsN, 0.617, 0.795, p);

    /* progress dashes */
    var di = p < 0.100 ? 0 : p < 0.360 ? 1 : p < 0.570 ? 2 : p < 0.830 ? 3 : 4;
    if (di !== dashIdx) {
      dashIdx = di;
      /* 히어로 구간 도달을 계측 스크립트에 알린다 (A·M·E·N·S). 수신부가 없어도 무해하다. */
      try { document.dispatchEvent(new CustomEvent('zg:hero-stage', { detail: { stage: 'AMENS'.charAt(di) } })); } catch (e) {}
      for (var dd = 0; dd < dashEls.length; dd++) dashEls[dd].classList.toggle('zg-on', dd === di);
    }

    /* camera: pushes in mid-beat, orbits opposite the pouch offset (three-quarter views),
       and drops low for an up-shot at night; pulls wide for the finale */
    camera.position.x = mouseX * 0.4 + Math.sin(t * 0.3) * 0.05 - 0.7 * w1 + 0.7 * w2;
    camera.position.z = 9.4 - zi * 2.1 + smooth(0.830, 0.947, p) * 1.3;
    camera.position.y = 0.7 - p * 0.25 - zi * 0.5 - 0.9 * w3;
    camera.lookAt(pouch.position.x * 0.5, -0.4 - p * 0.2 - zi * 0.55 + 0.45 * w3, 0);

    /* DOM 태양·달을 이번 프레임 카메라로 투영 */
    camera.updateMatrixWorld();
    camera.matrixWorldInverse.copy(camera.matrixWorld).invert();
    placeSky(sunDom, sun.position, sunSize, sunOp);
    placeSky(moonDom, moon.position, moonSize, moonOp);

    renderer.render(scene, camera);
  }
  frame();
  }

  var heroStarted = false;

  function startHero() {
    if (heroStarted) return;
    heroStarted = true;
    root.classList.remove('zg-no3d');
    initHero();                       /* WebGL 이 안 되면 안에서 다시 zg-no3d 를 붙인다 */
  }

  /* three.js 가 늦게 도착했을 때 — 사용자가 아직 맨 위(스크롤 0, iOS 바운스 여유 8px)면 3D 로 올린다.
     조금이라도 내려갔으면 폴백(100vh)을 그대로 둔다: 히어로가 386vh 로 늘어나며 스테이지가 위로 스냅하고
     아래 내용이 밀려 화면이 튄다 (실측 CLS: 0 에서만 0.006, 그 아래는 0.4~0.8). */
  function promoteIfNearTop() {
    if (typeof THREE === 'undefined') return;
    if ((window.pageYOffset || 0) > 8) return;
    startHero();
  }

  function boot() {
    root = document.querySelector('.zg-home');
    if (!root) return;
    var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced) root.classList.add('zg-reduced');
    initBar();
    initJump();
    if (typeof THREE !== 'undefined') { startHero(); return; }
    /* 아직 안 왔다 — 폴백으로 그려 두고 스크립트 태그의 load 를 기다린다 */
    root.classList.add('zg-no3d');
    var tag = document.querySelector('script[data-zg-three]');
    if (!tag) return;
    tag.addEventListener('load', promoteIfNearTop);
    /* error 는 폴백 유지 = 아무것도 안 한다 */
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();

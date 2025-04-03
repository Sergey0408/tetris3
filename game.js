
let scene, camera, renderer;
let squares = [];
let currentSquare = null;
let gameOver = false;
let startTime = null;

const GAME_WIDTH = 250;
const GAME_HEIGHT = 600;
const SQUARE_SIZE = 60;
const SECTORS = 4;
const SECTOR_WIDTH = GAME_WIDTH / SECTORS;

function init() {
    scene = new THREE.Scene();
    camera = new THREE.OrthographicCamera(
        GAME_WIDTH / -2, GAME_WIDTH / 2,
        GAME_HEIGHT / 2, GAME_HEIGHT / -2,
        1, 1000
    );
    camera.position.z = 100;

    renderer = new THREE.WebGLRenderer();
    renderer.setSize(302, GAME_HEIGHT);
    document.body.appendChild(renderer.domElement);

    createSquare();
    animate();
}

function createSquare() {
    const geometry = new THREE.BoxGeometry(SQUARE_SIZE, SQUARE_SIZE, 1);
    const color = new THREE.Color(Math.random(), Math.random(), Math.random());
    const material = new THREE.MeshBasicMaterial({ color: color });
    currentSquare = new THREE.Mesh(geometry, material);
    
    const sector = Math.floor(Math.random() * SECTORS);
    currentSquare.position.x = (sector * SECTOR_WIDTH) - (GAME_WIDTH / 2) + (SQUARE_SIZE / 2);
    currentSquare.position.y = (GAME_HEIGHT / 2) - (SQUARE_SIZE / 2);
    
    scene.add(currentSquare);
}

function animate() {
    requestAnimationFrame(animate);
    
    if (currentSquare && !gameOver) {
        currentSquare.position.y -= 2;
        
        if (currentSquare.position.y <= -(GAME_HEIGHT / 2) + (SQUARE_SIZE / 2)) {
            squares.push(currentSquare);
            createSquare();
        }
    }
    
    renderer.render(scene, camera);
}

document.addEventListener('keydown', (event) => {
    if (!currentSquare || gameOver) return;
    
    const moveAmount = SECTOR_WIDTH;
    if (event.key === 'ArrowLeft') {
        currentSquare.position.x -= moveAmount;
    } else if (event.key === 'ArrowRight') {
        currentSquare.position.x += moveAmount;
    }
    
    // Keep within bounds
    currentSquare.position.x = Math.max(
        -(GAME_WIDTH / 2) + (SQUARE_SIZE / 2),
        Math.min(GAME_WIDTH / 2 - (SQUARE_SIZE / 2), currentSquare.position.x)
    );
});

init();

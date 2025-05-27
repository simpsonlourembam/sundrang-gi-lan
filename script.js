const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

// Load images
const playerImage = new Image();
playerImage.src = 'kapthabi.png';

const enemyImage = new Image();
enemyImage.src = 'nungjao1.png'; // Using one asteroid image for now

const asteroidImage1 = new Image();
asteroidImage1.src = 'nungjao1.png';

const asteroidImage2 = new Image();
asteroidImage2.src = 'nungjao2.png';

// Load bullet image
const bulletImage = new Image();
bulletImage.src = 'maru.png';

// Keep track of loaded images
let imagesLoaded = 0;
const totalImages = 5; // Updated totalImages count

function imageLoaded() {
    imagesLoaded++;
    if (imagesLoaded === totalImages) {
        // All images are loaded, start the game loop
        console.log('All images loaded. Starting game...');
        gameLoop();
    }
}

// Add event listeners to images to count when they are loaded
playerImage.onload = imageLoaded;
enemyImage.onload = imageLoaded;
asteroidImage1.onload = imageLoaded;
asteroidImage2.onload = imageLoaded;
bulletImage.onload = imageLoaded;

// Add error handling for image loading (optional but recommended)
playerImage.onerror = () => { console.error('Error loading player image.'); };
enemyImage.onerror = () => { console.error('Error loading enemy image.'); };
asteroidImage1.onerror = () => { console.error('Error loading asteroid image 1.'); };
asteroidImage2.onerror = () => { console.error('Error loading asteroid image 2.'); };
bulletImage.onerror = () => { console.error('Error loading bullet image.'); };

// Keyboard and touch state
const keys = {};

window.addEventListener('keydown', (e) => {
    keys[e.key] = true;
    if (e.key === 'p' || e.key === 'P') {
        togglePause();
    }
});

window.addEventListener('keyup', (e) => {
    keys[e.key] = false;
});

// Handle touch controls
let touchStartX = null;
let touchStartY = null;

canvas.addEventListener('touchstart', (e) => {
    e.preventDefault(); // Prevent default touch behavior (like scrolling)
    const touch = e.touches[0];
    touchStartX = touch.clientX;
    touchStartY = touch.clientY;
    // Simple shooting on touch for now (can refine later)
    shoot();
});

canvas.addEventListener('touchmove', (e) => {
    e.preventDefault();
    const touch = e.touches[0];
    if (touchStartX !== null && touchStartY !== null) {
        // Calculate the difference in touch position to move the player
        const deltaX = touch.clientX - touchStartX;
        const deltaY = touch.clientY - touchStartY;

        player.x += deltaX;
        player.y += deltaY;

        // Prevent player from going out of bounds (re-apply bounds check from updatePlayerPosition)
        player.x = Math.max(player.width / 2, Math.min(canvas.width - player.width / 2, player.x));
        player.y = Math.max(player.height / 2, Math.min(canvas.height - player.height / 2, player.y));

        touchStartX = touch.clientX;
        touchStartY = touch.clientY;
    }
});

canvas.addEventListener('touchend', (e) => {
    e.preventDefault();
    touchStartX = null;
    touchStartY = null;
});

// Player state
const player = {
    x: canvas.width / 2,
    y: canvas.height - 50,
    width: 50, // Approximate width for the image
    height: 50, // Approximate height for the image
    color: 'gold',
    speed: 5,
    health: 100,
    maxHealth: 100,
};

function drawPlayer() {
    // Draw the player image, centered
    ctx.drawImage(playerImage, player.x - player.width / 2, player.y - player.height / 2, player.width, player.height);
}

// Bullet properties
const bullets = [];
const bulletSpeed = 7;
const bulletSize = 5;
const bulletColor = 'red';

// Destroyed asteroids counter
let destroyedAsteroids = 0;

class Bullet {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.width = 10; // Approximate width for the bullet image
        this.height = 20; // Approximate height for the bullet image
        this.speed = bulletSpeed;
    }

    update() {
        this.y -= this.speed;
    }

    draw() {
        // Draw bullet image, centered
        ctx.drawImage(bulletImage, this.x - this.width / 2, this.y - this.height / 2, this.width, this.height);
    }

    // Simple rectangle collision detection for bullets
    collidesWith(gameObject) {
        return this.x < gameObject.x + gameObject.width &&
               this.x + this.width > gameObject.x &&
               this.y < gameObject.y + gameObject.height &&
               this.y + this.height > gameObject.y;
    }
}

function shoot() {
    const bullet = new Bullet(player.x, player.y - player.height / 2); // Spawn bullet at top of player ship
    bullets.push(bullet);
}

// Asteroid properties
const asteroids = [];
const maxAsteroids = 20; // Increased asteroids
const asteroidSizeRange = { min: 30, max: 60 }; // Adjust size range for images
const asteroidColor = 'gray';

let gameState = 'playing'; // 'playing', 'gameOver', 'win'

class Asteroid {
    constructor(x, y, size) {
        this.x = x;
        this.y = y;
        this.width = size; // Use size for both width and height initially
        this.height = size;
        this.color = asteroidColor;
        this.speed = 0.5; // Asteroids move slowly downwards
    }

    update() {
        this.y += this.speed;
    }

    draw() {
        // Draw asteroid image, centered
        // For now, using asteroidImage1. Can add logic to randomly select later.
        ctx.drawImage(asteroidImage1, this.x - this.width / 2, this.y - this.height / 2, this.width, this.height);
    }

    collidesWith(gameObject) {
        // Simple rectangle collision detection
        return this.x < gameObject.x + gameObject.width &&
               this.x + this.width > gameObject.x &&
               this.y < gameObject.y + gameObject.height &&
               this.y + this.height > gameObject.y;
    }
}

function spawnAsteroid() {
    if (asteroids.length < maxAsteroids) {
        const size = Math.random() * (asteroidSizeRange.max - asteroidSizeRange.min) + asteroidSizeRange.min;
        const x = Math.random() * (canvas.width - size) + size / 2; // Adjust spawn x based on size
        const y = -size; // Spawn above the canvas
        const asteroid = new Asteroid(x, y, size);
        asteroids.push(asteroid);
    }
}

// Call spawnAsteroid initially to populate the screen with some asteroids
for (let i = 0; i < maxAsteroids; i++) {
    spawnAsteroid();
}

// Draw health and energy bars
function drawUI() {
    // Health bar
    ctx.fillStyle = 'red';
    ctx.fillRect(20, 20, player.health / player.maxHealth * 100, 10);
    ctx.strokeStyle = 'white';
    ctx.strokeRect(20, 20, 100, 10);
}

// Game state variables
let isPaused = false;

function togglePause() {
    isPaused = !isPaused;
    if (isPaused) {
        console.log('Game Paused');
        // TODO: Draw pause screen or message
    } else {
        console.log('Game Unpaused');
        // Request the next frame to resume the game loop
        requestAnimationFrame(gameLoop);
    }
}

// Automatic firing
const fireInterval = 1000 / 3; // 3 times per second
let lastFireTime = 0;

setInterval(() => {
    if (gameState === 'playing' && !isPaused) {
        shoot(); // Call shoot function every interval
    }
}, fireInterval);

// Asteroid spawning
const asteroidSpawnInterval = 1000; // Spawn an asteroid every second (adjust as needed)
let lastAsteroidSpawnTime = 0;
const initialAsteroids = 20; // Keep initial number for the count display, but spawn continuously

function gameLoop() {
    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw background
    drawStars();

    if (gameState === 'playing' && !isPaused) { // Update game state only if playing and not paused
        // Update game state (e.g., player position, enemy movement)
        updatePlayerPosition();

        // Update and draw bullets
        for (let i = bullets.length - 1; i >= 0; i--) {
            bullets[i].update();

            // Check for collisions with asteroids
            for (let j = asteroids.length - 1; j >= 0; j--) {
                if (bullets[i].collidesWith(asteroids[j])) {
                    // Collision detected
                    bullets.splice(i, 1); // Remove bullet
                    asteroids.splice(j, 1); // Remove asteroid
                    destroyedAsteroids++;
                    if (destroyedAsteroids >= maxAsteroids) { // Win condition: destroy all initial asteroids
                        gameState = 'win';
                    }
                    // Prevent checking the next bullet if the current one was removed
                    if (i < bullets.length) { // Check if the bullet at index i still exists
                         // If a bullet collides with an asteroid and is removed, the next bullet shifts down
                         // We need to adjust the outer loop index to avoid skipping a bullet
                         // This is a simple approach; for more complex scenarios, a different iteration method might be better
                    } else {
                       // If the last bullet was removed, the loop will terminate or continue correctly
                    }
                    break; // Only one asteroid can be hit per bullet for now
                }
            }

            // Remove bullets that are off-screen
            if (i >= 0 && bullets[i].y < 0) { // Check if the bullet still exists at index i
                bullets.splice(i, 1);
            }
        }

        // Update and draw asteroids
        for (let i = asteroids.length - 1; i >= 0; i--) {
            asteroids[i].update();

            // Check for collision with player
            if (asteroids[i].collidesWith(player)) {
                player.health -= 20; // Decrease health on collision (example value)
                if (player.health <= 0) {
                    gameState = 'gameOver';
                    console.log('Game Over!'); // Placeholder
                }
                asteroids.splice(i, 1); // Remove the asteroid on collision
            }

            // Remove asteroids that go off-screen
            if (asteroids[i].y > canvas.height) {
                asteroids.splice(i, 1);
            }
        }
    }

    // Draw game objects (e.g., background, player, enemies, asteroids) - Always draw
    drawPlayer();
    for (const bullet of bullets) {
        bullet.draw();
    }
    for (const asteroid of asteroids) {
        asteroid.draw();
    }

    // Draw UI elements
    drawObjective();
    drawUI();

    // Draw game state messages
    if (gameState === 'gameOver') {
        drawGameOver();
    } else if (gameState === 'win') {
        drawWin();
    }

    // Request the next frame only if playing
    if (gameState === 'playing') {
        requestAnimationFrame(gameLoop);
    }
}

// Start the game loop
// gameLoop(); // Game loop is now started after images are loaded

function updatePlayerPosition() {
    // Use arrow keys or WASD for movement
    if (keys['ArrowUp'] || keys['w'] || keys['W']) {
        player.y -= player.speed;
    }
    if (keys['ArrowDown'] || keys['s'] || keys['S']) {
        player.y += player.speed;
    }
    if (keys['ArrowLeft'] || keys['a'] || keys['A']) {
        player.x -= player.speed;
    }
    if (keys['ArrowRight'] || keys['d'] || keys['D']) {
        player.x += player.speed;
    }

    // Prevent player from going out of bounds
    player.x = Math.max(player.width / 2, Math.min(canvas.width - player.width / 2, player.x));
    player.y = Math.max(player.height / 2, Math.min(canvas.height - player.height / 2, player.y));
}

function drawObjective() {
    ctx.fillStyle = 'white';
    ctx.font = '20px Arial';
    ctx.fillText(`Asteroids Destroyed: ${destroyedAsteroids}`, 20, 40);
}

// Draw game over message
function drawGameOver() {
    ctx.fillStyle = 'white';
    ctx.font = '50px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Game Over!', canvas.width / 2, canvas.height / 2);
    ctx.textAlign = 'left'; // Reset text alignment
}

// Draw win message
function drawWin() {
    ctx.fillStyle = 'white';
    ctx.font = '50px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('You Win!', canvas.width / 2, canvas.height / 2);
    ctx.textAlign = 'left'; // Reset text alignment
}

// Draw stars for the background
function drawStars() {
    const numStars = 100;
    for (let i = 0; i < numStars; i++) {
        const x = Math.random() * canvas.width;
        const y = Math.random() * canvas.height;
        const size = Math.random() * 2;
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.arc(x, y, size / 2, 0, Math.PI * 2);
        ctx.fill();
    }
} 
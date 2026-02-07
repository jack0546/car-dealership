document.addEventListener('DOMContentLoaded', () => {
    // Navbar scroll effect
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Fetch and display featured cars on index
    const featuredContainer = document.getElementById('featured-cars');
    if (featuredContainer) {
        fetchCars(true);
    }

    // Fetch and display all cars on catalog
    const catalogContainer = document.getElementById('catalog-cars');
    if (catalogContainer) {
        fetchCars(false);
    }
});

// detect if we're running locally or on the web
const API_BASE_URL = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost'
    ? 'http://127.0.0.1:5000'
    : 'https://your-backend-api.onrender.com'; // Replace this after deploying to Render

async function fetchCars(featuredOnly = false) {
    const endpoint = featuredOnly ? `${API_BASE_URL}/api/cars?featured=true` : `${API_BASE_URL}/api/cars`;
    const containerId = featuredOnly ? 'featured-cars' : 'catalog-cars';
    const container = document.getElementById(containerId);

    try {
        console.log(`Fetching cars from: ${endpoint}`);
        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const cars = await response.json();
        console.log(`Successfully loaded ${cars.length} cars.`);

        container.innerHTML = ''; // Clear loading state

        if (cars.length === 0) {
            container.innerHTML = '<p class="text-muted">No vehicles found matching your criteria.</p>';
            return;
        }

        cars.forEach(car => {
            const card = createCarCard(car);
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error fetching cars:', error);
        container.innerHTML = `<p style="color: red;">Failed to load vehicles. Error: ${error.message}. Please ensure the backend is running at ${API_BASE_URL}</p>`;
    }
}

function createCarCard(car) {
    const div = document.createElement('div');
    div.className = 'car-card';
    div.innerHTML = `
        <div class="car-image">
            <img src="${car.image_url}" alt="${car.make} ${car.model}">
        </div>
        <div class="car-info">
            <span class="price">$${car.price.toLocaleString()}</span>
            <h3>${car.make} ${car.model}</h3>
            <p class="text-muted">${car.year} | ${car.fuel_type}</p>
            <div class="car-specs">
                <span>${car.mileage.toLocaleString()} mi</span>
                <span>${car.transmission}</span>
            </div>
            <a href="details.html?id=${car.id}" class="btn glass" style="width: 100%; margin-top: 1.5rem; text-align: center;">View Details</a>
        </div>
    `;
    return div;
}

// Enhanced Filter Functionality for Catalog
async function filterCars() {
    const make = document.getElementById('make-filter').value;
    const search = document.getElementById('search-input').value;
    const container = document.getElementById('catalog-cars');
    container.innerHTML = '<div class="loader">Loading...</div>';

    try {
        let url = `${API_BASE_URL}/api/cars?make=${make}`;
        if (search) {
            // Note: Simple frontend search extension or backend adjustment
            // For now, let's keep it simple and filter what's returned or 
            // adjust backend if necessary. Backend doesn't currently supports 'search' param.
            // Let's stick to 'make' for now as defined in backend or update backend.
        }
        const response = await fetch(url);
        let cars = await response.json();

        if (search) {
            cars = cars.filter(car =>
                car.model.toLowerCase().includes(search.toLowerCase()) ||
                car.make.toLowerCase().includes(search.toLowerCase())
            );
        }

        container.innerHTML = '';
        if (cars.length === 0) {
            container.innerHTML = '<p class="text-muted">No vehicles found matching your criteria.</p>';
            return;
        }
        cars.forEach(car => {
            container.appendChild(createCarCard(car));
        });
    } catch (error) {
        console.error('Filtering error:', error);
    }
}

// Add event listener for search input and global contact form
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            filterCars();
        });
    }

    const globalContactForm = document.getElementById('global-contact-form');
    if (globalContactForm) {
        globalContactForm.addEventListener('submit', handleGlobalInquiry);
    }
});

async function handleGlobalInquiry(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        name: formData.get('name'),
        email: formData.get('email'),
        message: `[Subject: ${formData.get('subject')}] ${formData.get('message')}`
    };

    try {
        const response = await fetch(`${API_BASE_URL}/api/inquiry`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (response.ok) {
            alert('Your message has been received! Our concierge team will contact you soon.');
            event.target.reset();
        } else {
            throw new Error('Server returned an error');
        }
    } catch (error) {
        console.error('Inquiry error:', error);
        alert('Submission failed. Please try again later or email us directly.');
    }
}

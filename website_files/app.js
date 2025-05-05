// Configuration
const config = {
    apiUrl: '/api', // This will be replaced with the actual API Gateway URL
    postsPerPage: 6
};

// State
let state = {
    posts: [],
    nextToken: null,
    loading: false
};

// DOM Elements
const postsContainer = document.getElementById('posts-container');
const loadMoreButton = document.getElementById('load-more');

// Event Listeners
document.addEventListener('DOMContentLoaded', init);
loadMoreButton.addEventListener('click', loadMorePosts);

// Initialize the application
async function init() {
    await fetchPosts();
    setupPostNavigation();
}

// Fetch posts from the API
async function fetchPosts(token = null) {
    if (state.loading) return;
    
    state.loading = true;
    showLoading(true);
    
    try {
        let url = `${config.apiUrl}/posts?limit=${config.postsPerPage}`;
        if (token) {
            url += `&nextToken=${encodeURIComponent(token)}`;
        }
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Failed to fetch posts');
        }
        
        const data = await response.json();
        
        // Update state
        state.posts = token ? [...state.posts, ...data.posts] : data.posts;
        state.nextToken = data.nextToken || null;
        
        // Render posts
        renderPosts();
        
        // Show/hide load more button
        loadMoreButton.style.display = state.nextToken ? 'block' : 'none';
    } catch (error) {
        console.error('Error fetching posts:', error);
        postsContainer.innerHTML = `
            <div class="error">
                <p>Failed to load posts. Please try again later.</p>
            </div>
        `;
    } finally {
        state.loading = false;
        showLoading(false);
    }
}

// Render posts to the DOM
function renderPosts() {
    if (state.posts.length === 0) {
        postsContainer.innerHTML = `
            <div class="no-posts">
                <p>No posts found.</p>
            </div>
        `;
        return;
    }
    
    const postsHTML = state.posts.map(post => `
        <article class="post-card">
            ${post.coverImage ? `
                <div class="post-image" style="background-image: url('${post.coverImage}')"></div>
            ` : ''}
            <div class="post-content">
                <h3><a href="/post.html?slug=${post.slug}">${post.title}</a></h3>
                <div class="post-meta">
                    ${post.author ? `By ${post.author} • ` : ''}
                    ${formatDate(post.createdAt)}
                </div>
                ${post.excerpt ? `
                    <div class="post-excerpt">
                        <p>${post.excerpt}</p>
                    </div>
                ` : ''}
                <a href="/post.html?slug=${post.slug}" class="read-more">Read More</a>
            </div>
        </article>
    `).join('');
    
    postsContainer.innerHTML = postsHTML;
}

// Load more posts when the button is clicked
function loadMorePosts() {
    if (state.nextToken) {
        fetchPosts(state.nextToken);
    }
}

// Show or hide loading indicator
function showLoading(show) {
    if (show) {
        if (state.posts.length === 0) {
            postsContainer.innerHTML = `<div class="loading">Loading posts...</div>`;
        }
        loadMoreButton.disabled = true;
        loadMoreButton.textContent = 'Loading...';
    } else {
        loadMoreButton.disabled = false;
        loadMoreButton.textContent = 'Load More';
    }
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Setup navigation for single post pages
function setupPostNavigation() {
    // Check if we're on a single post page
    const urlParams = new URLSearchParams(window.location.search);
    const slug = urlParams.get('slug');
    
    if (slug && window.location.pathname.includes('post.html')) {
        fetchSinglePost(slug);
    }
}

// Fetch a single post by slug
async function fetchSinglePost(slug) {
    const postContainer = document.getElementById('post-container');
    if (!postContainer) return;
    
    postContainer.innerHTML = `<div class="loading">Loading post...</div>`;
    
    try {
        const response = await fetch(`${config.apiUrl}/posts/${slug}`);
        if (!response.ok) {
            throw new Error('Failed to fetch post');
        }
        
        const post = await response.json();
        
        // Update page title
        document.title = `${post.title} - Serverless Blog Platform`;
        
        // Render post
        postContainer.innerHTML = `
            <article class="single-post">
                <header class="post-header">
                    <h2>${post.title}</h2>
                    <div class="post-meta">
                        ${post.author ? `By ${post.author} • ` : ''}
                        ${formatDate(post.createdAt)}
                    </div>
                </header>
                
                ${post.coverImage ? `
                    <div class="post-featured-image">
                        <img src="${post.coverImage}" alt="${post.title}">
                    </div>
                ` : ''}
                
                <div class="post-content">
                    ${post.content}
                </div>
                
                ${post.tags && post.tags.length > 0 ? `
                    <div class="post-tags">
                        <p>Tags: ${post.tags.map(tag => `<span class="tag">${tag}</span>`).join(' ')}</p>
                    </div>
                ` : ''}
            </article>
        `;
    } catch (error) {
        console.error('Error fetching post:', error);
        postContainer.innerHTML = `
            <div class="error">
                <p>Failed to load post. Please try again later.</p>
                <a href="/">Back to Home</a>
            </div>
        `;
    }
}
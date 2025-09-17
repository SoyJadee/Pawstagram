// Supabase configuration
export const supabaseConfig = {
    url: 'YOUR_SUPABASE_URL', // Replace with your Supabase URL
    anonKey: 'YOUR_SUPABASE_ANON_KEY', // Replace with your Supabase anon key
    
    // Database tables
    tables: {
        profiles: 'profiles',
        posts: 'posts',
        likes: 'likes',
        comments: 'comments',
        adoptions: 'adoptions',
        notifications: 'notifications',
        stores: 'stores',
        follows: 'follows'
    },
    
    // Storage buckets
    storage: {
        profiles: 'profile-images',
        posts: 'post-images',
        stores: 'store-images'
    }
};

// App configuration
export const appConfig = {
    name: 'Pawstagram',
    version: '1.0.0',
    
    // Feature flags
    features: {
        notifications: true,
        maps: true,
        stores: true,
        adoption: true
    },
    
    // UI configuration
    ui: {
        postsPerPage: 10,
        commentsPerPage: 5,
        notificationsPerPage: 15
    },
    
    // Map configuration
    maps: {
        defaultCenter: [40.7128, -74.0060], // NYC coordinates
        defaultZoom: 12,
        maxZoom: 18
    }
};
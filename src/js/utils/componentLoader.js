export async function loadComponent(containerId, componentPath) {
    try {
        const response = await fetch(`./src/components/${componentPath}.html`);
        if (!response.ok) {
            throw new Error(`Component not found: ${componentPath}`);
        }
        
        const html = await response.text();
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = html;
        }
        
        // Load component script if it exists
        try {
            const script = await import(`../components/${componentPath}.js`);
            if (script.init) {
                script.init();
            }
        } catch (error) {
            // Component script doesn't exist, which is fine
            console.log(`No script found for component: ${componentPath}`);
        }
        
        return true;
    } catch (error) {
        console.error('Error loading component:', error);
        return false;
    }
}
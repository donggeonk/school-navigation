class SearchComponent {
    constructor() {
        this.startInput = document.createElement('input');
        this.startInput.placeholder = 'Enter start location';
        
        this.destinationInput = document.createElement('input');
        this.destinationInput.placeholder = 'Enter destination location';
        
        this.searchButton = document.createElement('button');
        this.searchButton.innerText = 'Search';
        this.searchButton.addEventListener('click', () => this.handleSearch());

        this.container = document.createElement('div');
        this.container.appendChild(this.startInput);
        this.container.appendChild(this.destinationInput);
        this.container.appendChild(this.searchButton);
    }

    handleSearch() {
        const startLocation = this.startInput.value;
        const destinationLocation = this.destinationInput.value;
        // Trigger navigation logic here
        console.log(`Searching path from ${startLocation} to ${destinationLocation}`);
    }

    render() {
        return this.container;
    }
}

export default SearchComponent;
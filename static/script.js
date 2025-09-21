document.addEventListener('DOMContentLoaded', () => {
    const dataContainer = document.getElementById('data-container');
    const dataInput = document.getElementById('data-input');
    const addButton = document.getElementById('add-button');

    // Function to fetch and display data from the backend
    async function fetchData() {
        try {
            const response = await fetch('/api/data');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            renderData(data);
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }

    // Function to render the data in the UI
    function renderData(data) {
        dataContainer.innerHTML = '';
        if (data.length > 0) {
            data.forEach(item => {
                const listItem = document.createElement('li');
                listItem.textContent = `ID: ${item.id}, Data: ${item.content}`;
                dataContainer.appendChild(listItem);
            });
        } else {
            dataContainer.innerHTML = '<li>No data yet.</li>';
        }
    }

    // Function to send new data to the backend
    async function addData() {
        const content = dataInput.value.trim();
        if (content) {
            try {
                const response = await fetch('/api/add-data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ content: content }),
                });
                if (!response.ok) {
                    throw new Error('Failed to add data.');
                }
                const result = await response.json();
                console.log(result.message);
                dataInput.value = ''; // Clear the input field
                fetchData(); // Refresh the list
            } catch (error) {
                console.error('Error adding data:', error);
            }
        }
    }

    // Attach event listeners
    addButton.addEventListener('click', addData);

    // Initial data fetch
    fetchData();
});

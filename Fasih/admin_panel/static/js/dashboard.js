const chartCanvas = document.getElementById("specialistsChart");

if (chartCanvas) {
    const labels = JSON.parse(chartCanvas.dataset.labels);
    const specialists = JSON.parse(chartCanvas.dataset.values);
    const patients = JSON.parse(chartCanvas.dataset.patients);

    new Chart(chartCanvas, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "الأخصائيون",
                    data: specialists,
                    borderWidth: 2,
                    tension: 0.3
                },
                {
                    label: "المرضى",
                    data: patients,
                    borderWidth: 2,
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}
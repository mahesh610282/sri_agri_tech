document.addEventListener("DOMContentLoaded", () => {

    /* =========================
       SCROLL REVEAL
    ========================= */

    const observer = new IntersectionObserver(
        entries => {

            entries.forEach(entry => {

                if (entry.isIntersecting) {

                    entry.target.classList.add("visible");

                    observer.unobserve(entry.target);
                }

            });

        },
        {
            threshold: 0.12
        }
    );

    document
        .querySelectorAll(".reveal")
        .forEach(element => observer.observe(element));


    /* =========================
       AUTO CLOSE ALERTS
    ========================= */

    document
        .querySelectorAll(".alert")
        .forEach((alert, index) => {

            setTimeout(() => {

                if (alert.classList.contains("show")) {

                    const instance =
                        bootstrap.Alert.getOrCreateInstance(alert);

                    instance.close();
                }

            }, 5000 + index * 500);

        });

});
document.addEventListener("DOMContentLoaded", function () {

    const itemsContainer =
        document.getElementById("items");

    const addButton =
        document.getElementById("add-item");

    const grandTotal =
        document.getElementById("grand-total");

    const discountInput =
        document.getElementById("discount");


    function calculateTotal() {

        let subtotal = 0;

        const rows =
            document.querySelectorAll(".item-row");


        rows.forEach(function (row) {

            const product =
                row.querySelector(
                    ".product-select"
                );

            const quantity =
                row.querySelector(
                    ".quantity"
                );

            if (!product || !quantity) {
                return;
            }


            const selected =
                product.options[
                    product.selectedIndex
                ];


            if (!selected) {
                return;
            }


            const price =
                parseFloat(
                    selected.dataset.price || 0
                );


            const qty =
                parseFloat(
                    quantity.value || 0
                );


            subtotal += price * qty;

        });


        const discount =
            parseFloat(
                discountInput?.value || 0
            );


        const total =
            Math.max(
                subtotal - discount,
                0
            );


        if (grandTotal) {

            grandTotal.value =
                total.toFixed(2);

        }

    }


    function bindRow(row) {

        const product =
            row.querySelector(
                ".product-select"
            );

        const quantity =
            row.querySelector(
                ".quantity"
            );

        const removeButton =
            row.querySelector(
                ".remove"
            );


        if (product) {

            product.addEventListener(
                "change",
                calculateTotal
            );

        }


        if (quantity) {

            quantity.addEventListener(
                "input",
                calculateTotal
            );

        }


        if (removeButton) {

            removeButton.addEventListener(
                "click",
                function () {

                    const rows =
                        document.querySelectorAll(
                            ".item-row"
                        );


                    if (rows.length > 1) {

                        row.remove();

                    }

                    calculateTotal();

                }
            );

        }

    }


    if (itemsContainer) {

        const firstRow =
            itemsContainer.querySelector(
                ".item-row"
            );

        if (firstRow) {

            bindRow(firstRow);

        }

    }


    if (addButton) {

        addButton.addEventListener(
            "click",
            function () {

                const firstRow =
                    document.querySelector(
                        ".item-row"
                    );


                if (!firstRow) {
                    return;
                }


                const newRow =
                    firstRow.cloneNode(true);


                newRow
                    .querySelector(
                        ".product-select"
                    )
                    .selectedIndex = 0;


                newRow
                    .querySelector(
                        ".quantity"
                    )
                    .value = "";


                itemsContainer.appendChild(
                    newRow
                );


                bindRow(newRow);

            }
        );

    }


    if (discountInput) {

        discountInput.addEventListener(
            "input",
            calculateTotal
        );

    }


    calculateTotal();

});
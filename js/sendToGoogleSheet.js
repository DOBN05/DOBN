async function sendToGoogleSheet(formData){
    const scriptURL =
    "https://script.google.com/macros/s/AKfycbwzNi-cvJ8wQUidh7T9Qj4ka1VvXGUufiETqd3R0IqIAsGRpHv0PL0szOYMfjQGfiVDHA/exec";
    try{
        await fetch(scriptURL, {
            method: "POST",
            mode: "no-cors",  // ← thêm
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(formData)
        });
        console.log("Đã gửi dữ liệu lên Google Sheet");
    }
    catch(error){
        console.error(
            "Lỗi Google Sheet:",
            error
        );
    }
}

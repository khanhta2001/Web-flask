let delete_page = async function(id){
    const data = {answer : id};
    return fetch("/delete", {
        method: 'POST',
        headers: {
      'Content-Type': 'application/json'
        },
        redirect: 'follow',
        body: JSON.stringify(data)
    });
}
let deleted_rows = (function(i){
    const lists = document.getElementById(i);
    lists.remove();
})





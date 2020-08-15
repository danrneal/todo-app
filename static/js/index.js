const todoDels = document.querySelectorAll('.todo-del');
todoDels.forEach((todoDel) => {
  const delBtn = todoDel;
  delBtn.onclick = (event) => {
    const { todoId } = event.target.dataset;
    fetch(`/todos/${todoId}`, {
      method: 'DELETE',
    })
      .then(() => {
        const liItem = document.querySelector(`li[data-todo-id="${todoId}"]`);
        liItem.remove();
        document.getElementById('todo-error').className = 'hidden';
      })
      .catch(() => {
        document.getElementById('todo-error').className = '';
      });
  };
});

const checkboxes = document.querySelectorAll('.completed');
checkboxes.forEach((checkbox) => {
  const box = checkbox;
  box.onchange = (event) => {
    const completed = event.target.checked;
    const { todoId } = event.target.dataset;
    fetch(`/todos/${todoId}/edit`, {
      method: 'POST',
      body: JSON.stringify({ completed }),
      headers: { 'Content-type': 'application/json' },
    })
      .then(() => {
        document.getElementById('todo-error').className = 'hidden';
      })
      .catch(() => {
        document.getElementById('todo-error').className = '';
      });
  };
});

const completeAll = document.querySelector('#complete-all');
completeAll.onclick = (event) => {
  const { listId } = event.target.dataset;
  fetch(`/lists/${listId}/edit`, {
    method: 'POST',
  })
    .then(() => {
      checkboxes.forEach((checkbox) => {
        const box = checkbox;
        box.checked = true;
      });
      document.getElementById('todo-error').className = 'hidden';
    })
    .catch(() => {
      document.getElementById('todo-error').className = '';
    });
};

const listDels = document.querySelectorAll('.list-del');
listDels.forEach((listDel) => {
  const delBtn = listDel;
  delBtn.onclick = (event) => {
    const { listId } = event.target.dataset;
    fetch(`/lists/${listId}`, {
      method: 'DELETE',
    })
      .then(() => {
        if (listId === '{{ active_list.id }}') {
          window.location.replace('/');
        } else {
          const liItem = document.querySelector(`li[data-list-id="${listId}"]`);
          liItem.remove();
        }
        document.getElementById('list-error').className = 'hidden';
      })
      .catch(() => {
        document.getElementById('list-error').className = '';
      });
  };
});

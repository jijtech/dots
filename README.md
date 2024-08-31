<div style="display: flex;">
  <button style="padding: 10px; border: 1px solid #ccc; cursor: pointer; background-color: #ddd;">Tab 1</button>
  <button style="padding: 10px; border: 1px solid #ccc; cursor: pointer;">Tab 2</button>
  <button style="padding: 10px; border: 1px solid #ccc; cursor: pointer;">Tab 3</button>

  <div style="display: none;">Content for Tab 1</div>
  <div style="display: none;">Content for Tab 2</div>
  <div style="display: none;">Content for Tab 3</div>
</div>


<details>
<summary>Tab 1</summary>
<div>
**Content for Tab 1**
</div>
</details>

<details>
<summary>Tab 2</summary>
<div>
**Content for Tab 2**
</div>
</details>



<div class="tabs">
  <button class="tab-button active">Tab 1</button>
  <button class="tab-button">Tab 2</button>
  <button class="tab-button">Tab 3</button>

  <div   
 class="tab-content">
    <div class="tab-pane active">Content for Tab 1</div>
    <div class="tab-pane">Content for Tab 2</div>
    <div class="tab-pane">Content for Tab 3</div>
  </div>
</div>

<style>
  .tabs {
    display: flex;
  }

  .tab-button {
    padding: 10px;
    border: 1px solid #ccc;
    cursor: pointer;
  }

  .tab-button.active {
    background-color: #ddd;
  }

  .tab-content {
    display: none;
  }

  .tab-pane.active {
    display: block;
  }
</style>

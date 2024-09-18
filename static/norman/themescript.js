
    editor.BlockManager.add('bootstrap-header', {
        label: '<img src="https://via.placeholder.com/50x50.png?text=Header" alt="Header" /> Header',
        content: '<header class="bg-primary text-white text-center py-5"><h1>Welcome to LinkBay</h1></header>',
        category: 'Bootstrap'
    });

    editor.BlockManager.add('bootstrap-section', {
        label: '<img src="https://via.placeholder.com/50x50.png?text=Section" alt="Section" /> Section',
        content: '<section class="py-5"><div class="container"><div class="row"><div class="col-md-6"><h2>Section Title</h2><p>This is a sample section.</p></div><div class="col-md-6"><p>Another column in the section.</p></div></div></div></section>',
        category: 'Bootstrap'
    });

    editor.BlockManager.add('bootstrap-footer', {
        label: '<img src="https://via.placeholder.com/50x50.png?text=Footer" alt="Footer" /> Footer',
        content: '<footer class="bg-dark text-white text-center py-3"><p>&copy; 2024 LinkBay. All rights reserved.</p></footer>',
        category: 'Bootstrap'
    });

    editor.BlockManager.add('bootstrap-card', {
        label: '<img src="https://via.placeholder.com/50x50.png?text=Card" alt="Card" /> Card',
        content: '<div class="card" style="width: 18rem;"><img class="card-img-top" src="https://via.placeholder.com/150" alt="Card image cap"><div class="card-body"><h5 class="card-title">Card title</h5><p class="card-text">Some quick example text to build on the card title and make up the bulk of the card\'s content.</p><a href="#" class="btn btn-primary">Go somewhere</a></div></div>',
        category: 'Bootstrap'
    });

<?php

namespace App\Http\Controllers\V1;

use App\Http\Controllers\Controller;
use App\Models\Page;
use App\Services\PageService;
use Illuminate\Http\Request;

class GetByPageController extends Controller
{
    public function __construct(private PageService $service)
    {
        
    }

    public function __invoke(Page $page)
    {
        return $this->service->fetch($page);
    }
}

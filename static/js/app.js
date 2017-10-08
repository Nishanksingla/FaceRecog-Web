var app = angular.module("FaceRecog", ['ui.bootstrap','ngProgress']);

app.controller('recognizeCtrl', ['$scope', '$http', 'ngProgress', function ($scope, $http,ngProgress) {
    // debugger
    $scope.imageURL="";
    $scope.isCollapsed = true;
    $scope.errorMsg = null;
    $scope.isError=false;
    $scope.detectedFace=null;
    $scope.recognizedUser=null;

    $scope.closeAlert = function() {
        $scope.errorMsg = "";
        $scope.isError=false;
    };
    
    // ngProgress.height('.2em');
    // ngProgress.color('#fed136');

    $scope.recognizeByUrl = function () {
        debugger
        // JSON.stringify
        if($scope.isCollapsed == false)
            $scope.isCollapsed = true;
        var data = {"image_url":$scope.imageURL};
        var config = {headers: { 'Content-Type': 'application/json' }};
        debugger
        // $http.post('/recognizeByUrl', $.param(data), config)
        // .success(function (data) {
        //     debugger
        //     if(data.error){
        //         $scope.errorMsg = data.error;
        //         $scope.isError = true;
        //     }else{
        //         $scope.isCollapsed = false;
        //         $scope.detectedFace = data.image;
        //         $scope.recognizedUser = data.recognized_user;
        //         // $scope.$apply();
        //     };
        // })
        // .error(function (data, status, headers, config) {
        //     debugger
        // });
        ngProgress.start();
        $http.post('/recognizeByUrl', data, config)
        .then(
            function(response) {
                debugger
                if(response.data.error){
                    $scope.errorMsg = response.data.error;
                    $scope.isError = true;
                }else{
                    $scope.isCollapsed = false;
                    $scope.detectedFaces=response.data;
                    // $scope.detectedFace = response.data.image;
                    // $scope.recognizedUser = response.data.recognized_user;
                    // $scope.$applyAsync();
                    // return $scope.detectedFace;

                    // $scope.$apply();
                }
                ngProgress.complete();
            }, function(response) {
                debugger
                ngProgress.complete();
            }
        );

        debugger
    };

}]);
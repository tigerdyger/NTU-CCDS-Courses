function report = check_environment()
%CHECK_ENVIRONMENT Read-only MATLAB and image toolbox availability check.
report.matlab_version = version;
toolbox = ver('images');
report.image_toolbox_installed = ~isempty(toolbox);
report.image_toolbox_license = logical(license('test', 'image_toolbox'));
names = {'imread', 'im2double', 'im2gray', 'graythresh', ...
    'imbinarize', 'imfilter', 'conv2', 'imshow', 'exportgraphics'};
report.missing_functions = names(cellfun(@(name) isempty(which(name)), names));
report.ready = report.image_toolbox_installed ...
    && report.image_toolbox_license && isempty(report.missing_functions);
fprintf('MATLAB: %s\n', report.matlab_version);
fprintf('Image Processing Toolbox installed/licensed: %d / %d\n', ...
    report.image_toolbox_installed, report.image_toolbox_license);
fprintf('Missing functions: %s\n', strjoin(report.missing_functions, ', '));
fprintf('Ready for execution checks: %d\n', report.ready);
end

function report = check_environment()
%CHECK_ENVIRONMENT Read-only diagnostic; contains no assessed implementation.
% A successful availability check still requires a subsequent execution test.

report.matlab_version = version;
report.matlab_release = version('-release');
image_toolbox = ver('images');
report.image_toolbox_installed = ~isempty(image_toolbox);
report.image_toolbox_version = '';
if report.image_toolbox_installed
    report.image_toolbox_version = image_toolbox(1).Version;
end
report.image_toolbox_license = logical(license('test', 'image_toolbox'));

report.base = available_functions({ ...
    'imread', 'imwrite', 'rgb2gray', 'imshow', 'conv2', ...
    'fft2', 'ifft2', 'ginput', 'exportgraphics'});
report.image = available_functions({'imhist', 'histeq', 'medfilt2'});
report.legacy_geometry = available_functions({'maketform', 'imtransform'});
report.modern_geometry = available_functions({'projtform2d', 'imwarp', 'imref2d'});

legacy_ok = all(structfun(@(value) value, report.legacy_geometry));
modern_ok = all(structfun(@(value) value, report.modern_geometry));
report.ready_for_smoke_test = report.image_toolbox_installed ...
    && report.image_toolbox_license ...
    && all(structfun(@(value) value, report.base)) ...
    && all(structfun(@(value) value, report.image)) ...
    && (legacy_ok || modern_ok);

fprintf('MATLAB: %s\n', report.matlab_version);
fprintf('Image Processing Toolbox installed: %d\n', report.image_toolbox_installed);
fprintf('Image Processing Toolbox version: %s\n', report.image_toolbox_version);
fprintf('Image Processing Toolbox license available: %d\n', report.image_toolbox_license);
print_missing('Base functions', report.base);
print_missing('Image functions', report.image);
fprintf('Legacy geometry interface available: %d\n', legacy_ok);
fprintf('Modern geometry interface available: %d\n', modern_ok);
fprintf('Ready for execution smoke tests: %d\n', report.ready_for_smoke_test);
end

function result = available_functions(names)
result = struct();
for index = 1:numel(names)
    name = names{index};
    result.(name) = ~isempty(which(name));
end
end

function print_missing(label, availability)
names = fieldnames(availability);
missing = names(~structfun(@(value) value, availability));
if isempty(missing)
    fprintf('%s: available\n', label);
else
    fprintf('%s missing: %s\n', label, strjoin(missing, ', '));
end
end

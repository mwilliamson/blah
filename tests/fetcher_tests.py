import os
import subprocess
from contextlib import contextmanager

from nose.tools import istest, assert_equal, assert_raises
import mock

from blah.fetcher import fetch
from blah.repositories import Repository
from blah.files import mkdir_p, temporary_directory, write_file, read_file
from blah import systems

#~ @istest
def repository_is_used_if_uri_has_prefix():
    git = mock_vcs("git")
    hg = mock_vcs("hg")
    git_uri = "http://www.example.com/project.git"
    
    fetch("git+" + git_uri, "/tmp/project", systems=[hg, git])
    
    git.fetch.assert_called_once_with(mock.ANY, "/tmp/project")
    uri_arg = git.fetch.call_args[0][0]
    assert_equal("git", uri_arg.vcs)
    assert_equal(git_uri, uri_arg.repo_uri)
    assert_equal(None, uri_arg.revision)
    
def mock_vcs(name):
    vcs = mock.Mock()
    vcs.name = name
    return vcs

@istest
def error_is_raised_if_repository_uri_is_not_recognised():
    with temporary_directory() as directory:
        target = os.path.join(directory, "clone")
        original_uri = "asf+file:///tmp"
        assert_raises(RuntimeError, lambda: fetch(original_uri, target))

@istest
def can_fetch_git_repository_into_new_directory():
    with temporary_directory() as directory:
        target = os.path.join(directory, "clone")
        with temporary_git_repo() as git_repo:
            original_uri = "git+file://" + git_repo.working_directory
            fetch(original_uri, target)
            assert_equal("Run it.", read_file(os.path.join(target, "README")))
        
@istest
def can_update_git_repository_to_latest_version():
    with temporary_directory() as directory:
        target = os.path.join(directory, "clone")
        with temporary_git_repo() as git_repo:
            original_uri = "git+file://" + git_repo.working_directory
            fetch(original_uri, target)
            assert_equal("Run it.", read_file(os.path.join(target, "README")))
            
            add_commit_to_git_repo(git_repo)
            fetch(original_uri, target)
            assert_equal("Run away!", read_file(os.path.join(target, "README")))
        
@istest
def can_update_git_repository_to_specific_commit_using_hash_before_commit_name():
    with temporary_directory() as directory:
        target = os.path.join(directory, "clone")
        with temporary_git_repo() as git_repo:
            original_uri = "git+file://" + git_repo.working_directory
            add_commit_to_git_repo(git_repo)
            fetch(original_uri, target)
            assert_equal("Run away!", read_file(os.path.join(target, "README")))
            
            fetch(original_uri + "#master^", target)
            assert_equal("Run it.", read_file(os.path.join(target, "README")))
            
@istest
def can_clone_git_repository_to_specific_commit_using_hash_before_commit_name():
    with temporary_directory() as directory:
        target = os.path.join(directory, "clone")
        with temporary_git_repo() as git_repo:
            original_uri = "git+file://" + git_repo.working_directory
            add_commit_to_git_repo(git_repo)
            fetch(original_uri + "#master^", target)
            assert_equal("Run it.", read_file(os.path.join(target, "README")))
            
@istest
def can_clone_git_repository_to_specific_commit_using_hash_before_commit_name():
    with temporary_directory() as directory:
        target = os.path.join(directory, "clone")
        with temporary_git_repo() as git_repo:
            original_uri = "git+file://" + git_repo.working_directory
            add_commit_to_git_repo(git_repo)
            fetch(original_uri + "#master^", target)
            assert_equal("Run it.", read_file(os.path.join(target, "README")))
        
@istest
def origin_is_prefixed_to_git_commit_if_necessary():
    with temporary_directory() as directory:
        target = os.path.join(directory, "clone")
        with temporary_git_repo() as git_repo:
            original_uri = "git+file://" + git_repo.working_directory
            # master == origin/master
            fetch(original_uri, target)
            assert_equal("Run it.", read_file(os.path.join(target, "README")))
            
            add_commit_to_git_repo(git_repo)
            # If we checkout master rather than origin/master, we don't change revision
            fetch(original_uri + "#master", target)
            assert_equal("Run away!", read_file(os.path.join(target, "README")))
            
@istest
def error_is_raised_if_target_is_file():
    with temporary_directory() as directory:
        target = os.path.join(directory, "clone")
        write_file(target, "Nope")
        with temporary_git_repo() as git_repo:
            original_uri = "git+file://" + git_repo.working_directory
            assert_raises(RuntimeError, lambda: fetch(original_uri, target))
            
@istest
def git_fetch_raises_error_if_target_is_not_git_repository():
    with temporary_directory() as directory:
        target = os.path.join(directory, "clone")
        mkdir_p(target)
        with temporary_git_repo() as git_repo:
            original_uri = "git+file://" + git_repo.working_directory
            assert_raises(RuntimeError, lambda: fetch(original_uri, target))
            
@istest
def git_fetch_raises_error_if_target_is_checkout_of_different_repository():
    with temporary_directory() as directory:
        target = os.path.join(directory, "clone")
        with temporary_git_repo() as first_repo:
            with temporary_git_repo() as second_repo:
                fetch("git+file://" + first_repo.working_directory, target)
                assert_raises(RuntimeError,
                    lambda: fetch("git+file://" + second_repo.working_directory, target))

@istest
def can_fetch_hg_repository_into_new_directory():
    with temporary_directory() as directory:
        target = os.path.join(directory, "clone")
        with temporary_hg_repo() as hg_repo:
            original_uri = "hg+file://" + hg_repo.working_directory
            fetch(original_uri, target)
            assert_equal("Run it.", read_file(os.path.join(target, "README")))
            
@istest
def can_update_hg_repository_to_latest_version():
    with temporary_directory() as directory:
        target = os.path.join(directory, "clone")
        with temporary_hg_repo() as hg_repo:
            original_uri = "hg+file://" + hg_repo.working_directory
            fetch(original_uri, target)
            assert_equal("Run it.", read_file(os.path.join(target, "README")))
            
            add_commit_to_hg_repo(hg_repo)
            fetch(original_uri, target)
            assert_equal("Run away!", read_file(os.path.join(target, "README")))
            
@istest
def can_update_hg_repository_to_specific_commit_using_hash_before_commit_name():
    with temporary_directory() as directory:
        target = os.path.join(directory, "clone")
        with temporary_hg_repo() as hg_repo:
            original_uri = "hg+file://" + hg_repo.working_directory
            add_commit_to_hg_repo(hg_repo)
            fetch(original_uri, target)
            assert_equal("Run away!", read_file(os.path.join(target, "README")))
            
            fetch(original_uri + "#0", target)
            assert_equal("Run it.", read_file(os.path.join(target, "README")))
            
@istest
def hg_fetch_raises_error_if_target_is_checkout_of_different_repository():
    with temporary_directory() as directory:
        target = os.path.join(directory, "clone")
        with temporary_hg_repo() as first_repo:
            with temporary_hg_repo() as second_repo:
                fetch("hg+file://" + first_repo.working_directory, target)
                assert_raises(RuntimeError,
                    lambda: fetch("hg+file://" + second_repo.working_directory, target))
        
@contextmanager
def temporary_git_repo():
    with temporary_directory() as path:
        repository = Repository(os.path.join(path, ".git"), "git")
        repository.execute(["init"])
        write_file(os.path.join(path, "README"), "Run it.")
        repository.execute(["add", "README"])
        repository.execute(["commit", "-mAdding README"])
        yield repository

def add_commit_to_git_repo(repo):
    write_file(os.path.join(repo.working_directory, "README"), "Run away!")
    repo.execute(["add", "README"])
    repo.execute(["commit", "-mUpdating README"])
        
@contextmanager
def temporary_hg_repo():
    with temporary_directory() as path:
        repository = Repository(os.path.join(path, ".hg"), "hg")
        repository.execute(["init"])
        write_file(os.path.join(path, "README"), "Run it.")
        repository.execute(["add", "README"])
        repository.execute(["commit", "-mAdding README"])
        yield repository

def add_commit_to_hg_repo(repo):
    write_file(os.path.join(repo.working_directory, "README"), "Run away!")
    repo.execute(["add", "README"])
    repo.execute(["commit", "-mUpdating README"])
